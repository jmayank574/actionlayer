"""Batched multi-label tagger: calls Claude per batch of reviews, validates
output against taxonomy.yaml, and returns tags + confidence per review.

Design choices:
- The model returns subcategory_id + confidence only; parent_category_id is
  always derived from our own taxonomy.yaml lookup, never trusted from model
  output — this eliminates an entire class of "parent doesn't match
  subcategory" bugs by construction.
- Any subcategory_id the model returns that isn't a real taxonomy id is
  dropped and counted as a validation issue, not silently kept.
- Batches that fail to parse/error out are retried with backoff; if still
  failing, every review_id in that batch is recorded as a failure with a
  reason — never silently dropped.
"""

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
from dotenv import load_dotenv

from tagging.prompt import build_batch_user_message

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS_PER_BATCH = 4000
BATCH_SIZE = 8
MAX_CONCURRENCY = 6
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 3

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _call_batch_once(system_prompt: str, reviews: list[dict]) -> dict:
    client = _get_client()
    user_message = build_batch_user_message(reviews)

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_PER_BATCH,
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_message}],
    )
    raw = _strip_fences(message.content[0].text)
    return json.loads(raw)


def tag_batch(system_prompt: str, reviews: list[dict], parent_lookup: dict[str, str], valid_ids: set[str]) -> dict:
    """Returns {
        "tagged": {review_id: [{"subcategory_id", "parent_id", "confidence"}, ...]},
        "invalid_ids_dropped": int,
        "unexpected_review_ids_dropped": int,     # model returned a review_id we never asked about
        "missing_review_ids": [review_id, ...],   # requested but not in response
        "failed_review_ids": [review_id, ...],    # batch never parsed after retries
        "failure_reason": str | None,
    }"""
    requested_ids = {str(r["review_id"]) for r in reviews}
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            parsed = _call_batch_once(system_prompt, reviews)
            results = parsed["results"]

            tagged = {}
            invalid_dropped = 0
            unexpected_dropped = 0
            seen_ids = set()

            for item in results:
                rid = str(item["review_id"])
                if rid not in requested_ids:
                    # Model returned an id we never asked about in this batch
                    # (hallucinated/duplicated) — drop it, don't let it inflate
                    # coverage counts for a review that was never processed.
                    unexpected_dropped += 1
                    continue
                seen_ids.add(rid)
                clean_tags = []
                for t in item.get("tags", []):
                    sub_id = t.get("subcategory_id")
                    if sub_id not in valid_ids:
                        invalid_dropped += 1
                        continue
                    clean_tags.append({
                        "subcategory_id": sub_id,
                        "parent_id": parent_lookup[sub_id],
                        "confidence": t.get("confidence", "medium"),
                    })
                tagged[rid] = clean_tags

            missing = list(requested_ids - seen_ids)
            return {
                "tagged": tagged,
                "invalid_ids_dropped": invalid_dropped,
                "unexpected_review_ids_dropped": unexpected_dropped,
                "missing_review_ids": missing,
                "failed_review_ids": [],
                "failure_reason": None,
            }
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
            continue

    return {
        "tagged": {},
        "invalid_ids_dropped": 0,
        "unexpected_review_ids_dropped": 0,
        "missing_review_ids": [],
        "failed_review_ids": list(requested_ids),
        "failure_reason": f"{type(last_error).__name__}: {last_error}",
    }


def tag_all(system_prompt: str, all_reviews: list[dict], parent_lookup: dict[str, str], valid_ids: set[str],
            batch_size: int = BATCH_SIZE, max_concurrency: int = MAX_CONCURRENCY, on_batch_done=None) -> dict:
    """Runs tag_batch across all_reviews in parallel batches.

    Returns {
        "tagged": {review_id: [...]},
        "invalid_ids_dropped_total": int,
        "unexpected_review_ids_dropped_total": int,
        "missing_review_ids": [...],
        "failed_review_ids": [...],
        "failure_reasons": {review_id_batch_key: reason},
    }"""
    batches = [all_reviews[i:i + batch_size] for i in range(0, len(all_reviews), batch_size)]

    all_tagged = {}
    invalid_total = 0
    unexpected_total = 0
    all_missing = []
    all_failed = []
    failure_reasons = {}

    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = {executor.submit(tag_batch, system_prompt, batch, parent_lookup, valid_ids): batch for batch in batches}
        for future in as_completed(futures):
            batch = futures[future]
            result = future.result()
            all_tagged.update(result["tagged"])
            invalid_total += result["invalid_ids_dropped"]
            unexpected_total += result["unexpected_review_ids_dropped"]
            all_missing.extend(result["missing_review_ids"])
            all_failed.extend(result["failed_review_ids"])
            if result["failure_reason"]:
                key = f"batch_starting_{batch[0]['review_id']}"
                failure_reasons[key] = result["failure_reason"]
            if on_batch_done:
                on_batch_done(len(all_tagged), len(all_reviews))

    return {
        "tagged": all_tagged,
        "invalid_ids_dropped_total": invalid_total,
        "unexpected_review_ids_dropped_total": unexpected_total,
        "missing_review_ids": all_missing,
        "failed_review_ids": all_failed,
        "failure_reasons": failure_reasons,
    }
