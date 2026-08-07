"""Assembles the system prompt for the tagger: taxonomy definitions/includes/
excludes + curated few-shot examples + output-format instructions.

This system prompt is identical across every batch call, so it's marked for
prompt caching (cache_control) — it's several thousand tokens and gets reused
across ~400 batched calls for the full 3,295-review run.
"""

from tagging.few_shot import build_few_shot_examples, render_few_shot_text
from tagging.taxonomy_loader import load_taxonomy, render_taxonomy_text, subcategory_to_parent_map

INSTRUCTIONS = """
# Your task

You are tagging real WHOOP (fitness wearable) customer reviews against the
taxonomy above. For each review, output zero or more subcategory tags.

Rules:
- Tag by subcategory id only (e.g. "price_value_perception") — you do not
  need to name the parent, it will be derived automatically.
- Multi-label is the norm, not an exception: many reviews raise 2-3 distinct
  issues in one paragraph. Tag every subcategory that genuinely applies.
- If nothing in the taxonomy fits — including generic undifferentiated praise
  like "5 stars" or "love it" with no specific feature/issue named — output an
  empty tags list. Do NOT force a tag onto a review just to give it one. Vague
  praise with no named topic is exactly what should get zero tags.
- Use the "Excludes / boundary" text for each subcategory to resolve
  borderline cases — that text exists specifically to prevent the confusions
  a naive read would make (see the worked examples below for concrete cases).
- Assign a confidence to each tag: "high" (clear, unambiguous fit), "medium"
  (fits, but could plausibly be read differently), or "low" (genuinely
  uncertain — flag it as low rather than omitting it or overstating certainty).
- Only use subcategory ids that appear in the taxonomy above, spelled exactly
  as given. Do not invent ids.

# Output format

Respond with ONLY a JSON object, no markdown fences, no explanation, in this
exact shape:

{
  "results": [
    {
      "review_id": "<the review_id you were given>",
      "tags": [
        {"subcategory_id": "price_value_perception", "confidence": "high"}
      ]
    }
  ]
}

"tags" must be present for every review_id you were given, even if it's an
empty list ([]). Every review_id you were given must appear exactly once in
"results".
""".strip()


def build_system_prompt() -> tuple[str, dict[str, str]]:
    """Returns (system_prompt_text, subcategory_to_parent_lookup)."""
    taxonomy = load_taxonomy()
    parent_lookup = subcategory_to_parent_map(taxonomy)

    taxonomy_text = render_taxonomy_text(taxonomy)
    examples = build_few_shot_examples()
    few_shot_text = render_few_shot_text(examples, parent_lookup)

    system_prompt = f"{taxonomy_text}\n{few_shot_text}\n{INSTRUCTIONS}"
    return system_prompt, parent_lookup


def build_batch_user_message(reviews: list[dict]) -> str:
    """reviews: list of {review_id, source, rating, text}."""
    lines = ["Tag the following reviews. Return results for every review_id below.\n"]
    for r in reviews:
        lines.append(f'review_id: {r["review_id"]}')
        lines.append(f'[{r["source"]}, {r["rating"]}-star]')
        lines.append(f'"{r["text"]}"')
        lines.append("")
    return "\n".join(lines)
