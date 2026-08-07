import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

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


def scrape_public_feedback(company_name: str, product_name: str) -> list[dict]:
    """Use Claude to simulate 25 realistic public feedback entries for a product."""
    client = _get_client()

    prompt = f"""Generate exactly 25 realistic public feedback entries about "{product_name}" by {company_name}.

These should be representative of what real users write on review platforms like G2, Reddit, App Store, Twitter, and Capterra.
Include a mix of sentiments, but lean toward real pain points users commonly report — be specific to actual features of {product_name}.

Return a JSON array of exactly 25 objects with these exact fields:
- "id": string like "fb-1", "fb-2", ... "fb-25"
- "subject": string — short title 5-10 words
- "description": string — the actual user feedback, 1-3 sentences in first person, realistic and specific
- "source": one of exactly: "g2", "reddit", "app_store", "twitter", "capterra"
- "sentiment": one of: "positive", "negative", "mixed"
- "status": "open"
- "priority": "normal"

Distribute sources roughly: 6 g2, 6 reddit, 6 app_store, 4 twitter, 3 capterra.
Make the descriptions feel authentic — include specific feature names, realistic frustrations, and genuine praise.
Focus on themes an engineering team could act on.

Return ONLY valid JSON — no markdown fences, no explanation, just the array."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = _strip_fences(message.content[0].text)
    items = json.loads(raw)

    for i, item in enumerate(items):
        item.setdefault("id", f"fb-{i + 1}")
        item.setdefault("status", "open")
        item.setdefault("priority", "normal")

    return items
