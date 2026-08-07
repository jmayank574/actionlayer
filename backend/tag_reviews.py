"""Runs the multi-label tagger against data/whoop_reviews_raw.csv and writes
data/tagged_reviews.csv (ActionLayer v2, step 3, Part 1).

Never reads data/eval_sample.csv — few-shot examples come only from
data/open_coding.csv (the 180 reviews used to BUILD the taxonomy).

Incremental by default: only review_ids not already present in
data/tagged_reviews.csv (or previously marked FAILED) are sent to Claude.
Everything already tagged is carried forward untouched. This matters because
ingest.py now runs daily and the raw dataset only grows a handful of reviews
per day -- re-tagging the whole multi-thousand-review corpus on every run
would spend real API money for no new signal. Use --full after a taxonomy
change, when every review genuinely needs to be re-evaluated against the new
categories.

Run with: python tag_reviews.py            (incremental: only new/failed reviews)
          python tag_reviews.py --full      (force re-tag of everything)
          python tag_reviews.py --limit 24  (small smoke test, still incremental)
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from tagging.prompt import build_system_prompt
from tagging.tagger import tag_all
from tagging.taxonomy_loader import load_taxonomy, valid_subcategory_ids

DATA_DIR = Path(__file__).parent / "data"
RAW_PATH = DATA_DIR / "whoop_reviews_raw.csv"
OUT_PATH = DATA_DIR / "tagged_reviews.csv"
STATS_PATH = DATA_DIR / "tag_run_stats.json"

# Reference rates from the 180-review hand-labeled sample (data/taxonomy_notes.md).
# NOTE: data/eval_sample.csv is NOT hand-labeled yet (confirmed 0/180 before this
# run), so there is only ONE real reference point here, not two — flagged
# explicitly in the stats output rather than silently treating this as "both
# samples agree."
REFERENCE_OTHER_RATE = (0.10, 0.15)
REFERENCE_MULTI_LABEL_RATE = 0.35, 0.40


def load_reviews(limit: int | None) -> list[dict]:
    df = pd.read_csv(RAW_PATH)
    if limit:
        df = df.head(limit)
    reviews = []
    for _, r in df.iterrows():
        reviews.append({
            "review_id": str(r["review_id"]),
            "source": r["source"],
            "rating": int(r["rating"]) if pd.notna(r["rating"]) else None,
            "date": r["date"],
            "text": str(r["text"]),
            "app_version": r.get("app_version"),
            "country": r.get("country"),
        })
    return reviews


def load_existing_tagged(path: Path) -> dict[str, dict]:
    """review_id -> its row from a prior tag_reviews.py run, exactly as last
    written (kept as raw strings so carrying a row forward unchanged is a
    byte-for-byte passthrough, not a lossy re-parse)."""
    if not path.exists():
        return {}
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return {row["review_id"]: row.to_dict() for _, row in df.iterrows()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only consider the first N raw reviews (smoke test)")
    parser.add_argument("--full", action="store_true", help="Force re-tagging of every review, not just new/failed ones")
    args = parser.parse_args()

    taxonomy = load_taxonomy()
    valid_ids = valid_subcategory_ids(taxonomy)
    system_prompt, parent_lookup = build_system_prompt()
    print(f"System prompt built: {len(system_prompt):,} chars, {len(valid_ids)} valid subcategory ids")

    reviews = load_reviews(args.limit)
    existing = {} if args.full else load_existing_tagged(OUT_PATH)

    def needs_tagging(review_id: str) -> bool:
        prior = existing.get(review_id)
        return prior is None or prior.get("status") == "FAILED"

    to_tag = [r for r in reviews if needs_tagging(r["review_id"])]
    carried_over = len(reviews) - len(to_tag)
    print(
        f"{len(reviews)} reviews in raw dataset" + (f" (limited to {args.limit})" if args.limit else "") + ". "
        + (f"Forcing full re-tag." if args.full
           else f"{carried_over} already tagged (carried forward, no API call), {len(to_tag)} need tagging.")
    )

    review_by_id = {r["review_id"]: r for r in to_tag}

    def progress(done, total):
        print(f"  ... {done}/{total} reviews tagged so far", flush=True)

    if to_tag:
        print("Pass 1: batched tagging...")
        result = tag_all(system_prompt, to_tag, parent_lookup, valid_ids, on_batch_done=progress)

        retry_pool_ids = set(result["missing_review_ids"]) | set(result["failed_review_ids"])
        all_failure_reasons = dict(result["failure_reasons"])
        unexpected_total = result["unexpected_review_ids_dropped_total"]

        if retry_pool_ids:
            print(f"Pass 2: retrying {len(retry_pool_ids)} missing/failed review(s) individually...")
            retry_reviews = [review_by_id[rid] for rid in retry_pool_ids if rid in review_by_id]
            retry_result = tag_all(system_prompt, retry_reviews, parent_lookup, valid_ids, batch_size=1, max_concurrency=4)
            result["tagged"].update(retry_result["tagged"])
            result["invalid_ids_dropped_total"] += retry_result["invalid_ids_dropped_total"]
            unexpected_total += retry_result["unexpected_review_ids_dropped_total"]
            all_failure_reasons.update(retry_result["failure_reasons"])
            still_missing = set(retry_result["missing_review_ids"]) | set(retry_result["failed_review_ids"])
        else:
            still_missing = set()
    else:
        print("Nothing new to tag -- every review is already tagged.")
        result = {"tagged": {}, "invalid_ids_dropped_total": 0, "unexpected_review_ids_dropped_total": 0}
        all_failure_reasons = {}
        unexpected_total = 0
        still_missing = set()

    tagged = result["tagged"]
    all_requested_ids = set(review_by_id.keys())
    # Coverage is the intersection with what was actually requested — a
    # defensive check against any batch-key collision, not just len(tagged).
    # Scoped to this run's batch (to_tag), not the whole raw dataset, since
    # carried-forward reviews were never requested this run.
    covered = len(all_requested_ids & tagged.keys())
    total_this_run = len(to_tag)
    coverage_pct = covered / total_this_run * 100 if total_this_run else 100.0

    print(f"\nThis run's coverage: {covered}/{total_this_run} ({coverage_pct:.1f}%)")
    if still_missing:
        print(f"UNTAGGED after retry ({len(still_missing)}): {sorted(still_missing)[:20]}{'...' if len(still_missing) > 20 else ''}")
        for rid in still_missing:
            all_failure_reasons.setdefault(rid, "no result returned after batched + individual retry")

    # --- Write tagged_reviews.csv, preserving review_id, source, rating, date ---
    rows = []
    for r in reviews:
        rid = r["review_id"]
        tags = tagged.get(rid)
        if tags is not None:
            rows.append({
                "review_id": rid, "source": r["source"], "rating": r["rating"], "date": r["date"],
                "text": r["text"],
                "parent_category_tags": ";".join(t["parent_id"] for t in tags),
                "subcategory_tags": ";".join(t["subcategory_id"] for t in tags),
                "confidences": ";".join(t["confidence"] for t in tags),
                "tag_count": len(tags),
                "status": "OK",
            })
        elif rid in review_by_id:
            # Was sent to Claude this run (to_tag) but never came back tagged,
            # even after the individual retry pass -- a genuine failure.
            rows.append({
                "review_id": rid, "source": r["source"], "rating": r["rating"], "date": r["date"],
                "text": r["text"],
                "parent_category_tags": "", "subcategory_tags": "", "confidences": "",
                "tag_count": "", "status": "FAILED",
            })
        else:
            # Not attempted this run at all -- carry the prior result forward
            # byte-for-byte. tag_count is re-cast to int (CSV round-trips it as
            # a string) so it still matches the OK-row shape for the stats
            # block below, instead of silently falling out of other/multi
            # counts because "2" != 2.
            prior = existing[rid]
            prior_tag_count = prior["tag_count"]
            rows.append({
                "review_id": prior["review_id"], "source": prior["source"], "rating": prior["rating"],
                "date": prior["date"], "text": prior["text"],
                "parent_category_tags": prior["parent_category_tags"],
                "subcategory_tags": prior["subcategory_tags"],
                "confidences": prior["confidences"],
                "tag_count": int(prior_tag_count) if prior_tag_count not in ("", None) else "",
                "status": prior["status"],
            })

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_PATH}")

    # --- Run stats ---
    ok_rows = [r for r in rows if r["status"] == "OK"]
    other_count = sum(1 for r in ok_rows if r["tag_count"] == 0)
    multi_count = sum(1 for r in ok_rows if isinstance(r["tag_count"], int) and r["tag_count"] >= 2)
    other_rate = other_count / len(ok_rows) if ok_rows else 0
    multi_rate = multi_count / len(ok_rows) if ok_rows else 0

    other_flag = not (REFERENCE_OTHER_RATE[0] <= other_rate <= REFERENCE_OTHER_RATE[1])
    multi_flag = not (REFERENCE_MULTI_LABEL_RATE[0] <= multi_rate <= REFERENCE_MULTI_LABEL_RATE[1])

    stats = {
        "total_reviews": len(reviews),
        "newly_tagged_this_run": len(to_tag),
        "carried_over_this_run": carried_over,
        "tagged_ok": len(ok_rows),
        "failed": len(rows) - len(ok_rows),
        "coverage_pct_this_run": round(coverage_pct, 2),
        "invalid_subcategory_ids_dropped": result["invalid_ids_dropped_total"],
        "unexpected_review_ids_dropped": unexpected_total,
        "other_ungrouped_count": other_count,
        "other_ungrouped_rate": round(other_rate, 4),
        "other_ungrouped_reference_range": REFERENCE_OTHER_RATE,
        "other_ungrouped_out_of_reference_range": other_flag,
        "multi_label_count": multi_count,
        "multi_label_rate": round(multi_rate, 4),
        "multi_label_reference_range": REFERENCE_MULTI_LABEL_RATE,
        "multi_label_out_of_reference_range": multi_flag,
        "note_on_reference_rates": (
            "Reference rates come from data/taxonomy_sample.csv's 180-review hand-labeled "
            "pass ONLY. data/eval_sample.csv was NOT hand-labeled at the time of this run "
            "(0/180), so there is one real reference point here, not two."
        ),
        "failure_reasons": all_failure_reasons,
    }

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n=== RUN STATS ===")
    print(json.dumps(stats, indent=2))

    if other_flag:
        print(f"\n*** FLAG: Other/Ungrouped rate {other_rate:.1%} is outside the "
              f"{REFERENCE_OTHER_RATE[0]:.0%}-{REFERENCE_OTHER_RATE[1]:.0%} reference range "
              f"from the 180-review sample. Investigate before trusting this run. ***")
    if multi_flag:
        print(f"\n*** FLAG: Multi-label rate {multi_rate:.1%} is outside the "
              f"{REFERENCE_MULTI_LABEL_RATE[0]:.0%}-{REFERENCE_MULTI_LABEL_RATE[1]:.0%} reference range "
              f"from the 180-review sample. Investigate before trusting this run. ***")


if __name__ == "__main__":
    main()
