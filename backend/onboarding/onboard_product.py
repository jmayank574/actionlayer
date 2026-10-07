"""Onboarding agent for a new product (roadmap step 5). Reuses the exact
same ingestion and sampling building blocks already proven on WHOOP
(ingestion/google_play.py, ingestion/app_store.py, ingestion/normalize.py,
ingestion/merge.py, sample_for_taxonomy.py's stratified_sample) -- nothing
here is a parallel reimplementation.

What it does, for a brand-new product:
  1. Ingest a real pull of Google Play + App Store reviews
  2. Draw a stratified open-coding sample (same method as WHOOP's taxonomy)
  3. Ask Claude to draft a bottom-up taxonomy from that real sample, in the
     same YAML schema as data/taxonomy.yaml, citing real sample_ids
  4. Carve out an eval seed (for a human to hand-label later -- an eval set
     that labels itself isn't an independent check of anything)
  5. Write one onboarding report tying it together

What it never does: touch WHOOP's data, write anything into
backend/data/taxonomy.yaml, or call the tagger. Everything lands under
backend/data/products/<slug>/ as a draft. Per the roadmap rule ("it proposes
via PR/issue, you approve"), turning the draft into the live taxonomy for
this product is a deliberate, separate, human-reviewed step.

Run with (from backend/):
  python -m onboarding.onboard_product \\
      --product-name "Oura Ring" --category "Wearables & Fitness" \\
      --google-play-package com.ouraring.oura --app-store-id 1043837948
"""

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import yaml

from ingestion.app_store import fetch_app_store_reviews
from ingestion.google_play import fetch_google_play_reviews
from ingestion.merge import load_existing, merge_upsert
from ingestion.normalize import SCHEMA_FIELDS, clean_and_dedupe, normalize_app_store, normalize_google_play
from ingestion.report import build_summary, render_markdown
from sample_for_taxonomy import stratified_sample

BACKEND_DIR = Path(__file__).parent.parent
PRODUCTS_DIR = BACKEND_DIR / "data" / "products"

EVAL_SEED_SIZE = 40
N_TIME_BUCKETS = 3


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def ingest(slug: str, gp_package: str | None, as_id: str | None, country: str) -> tuple[pd.DataFrame, str]:
    product_dir = PRODUCTS_DIR / slug
    product_dir.mkdir(parents=True, exist_ok=True)
    csv_path = product_dir / "reviews_raw.csv"

    all_issues: list[str] = []
    gp_raw, as_raw = [], []

    if gp_package:
        print(f"Fetching Google Play reviews for {gp_package} ...")
        gp_raw, gp_issues = fetch_google_play_reviews(gp_package, country=country)
        all_issues += gp_issues
        print(f"  -> {len(gp_raw)} raw reviews")

    if as_id:
        print(f"Fetching Apple App Store reviews for id{as_id} ...")
        as_raw, as_issues = fetch_app_store_reviews(as_id, country=country)
        all_issues += as_issues
        print(f"  -> {len(as_raw)} raw reviews")

    rows = normalize_google_play(gp_raw, country) + normalize_app_store(as_raw, country)
    kept_rows, drop_counts = clean_and_dedupe(rows)

    existing = load_existing(csv_path)
    merged_rows, merge_counts = merge_upsert(existing, kept_rows)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        import csv as csv_module
        writer = csv_module.DictWriter(f, fieldnames=SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerows(merged_rows)
    print(f"Wrote {len(merged_rows)} reviews to {csv_path}")

    summary = build_summary(slug, merged_rows, drop_counts, all_issues, merge_counts)
    report_md = render_markdown(summary)
    (product_dir / "ingest_report.md").write_text(report_md, encoding="utf-8")

    return pd.DataFrame(merged_rows), report_md


def draw_sample(slug: str, df: pd.DataFrame, sample_size: int) -> pd.DataFrame:
    df = df.copy()
    df["date_parsed"] = pd.to_datetime(df["date"], format="mixed", utc=True)

    sources = df["source"].unique().tolist()
    per_source_target = max(1, sample_size // max(1, len(sources)))

    picked = []
    for source in sources:
        src_df = df[df["source"] == source]
        picked.append(stratified_sample(src_df, "rating", "date_parsed", per_source_target, N_TIME_BUCKETS))

    sample = pd.concat(picked).drop(columns=["date_parsed"]).drop_duplicates(subset=["review_id", "text"])
    sample = sample.sample(frac=1, random_state=42).reset_index(drop=True)
    sample.insert(0, "sample_id", range(1, len(sample) + 1))

    out_path = PRODUCTS_DIR / slug / "taxonomy_sample.csv"
    sample.to_csv(out_path, index=False)
    print(f"Wrote {len(sample)} sampled reviews to {out_path}")
    return sample


def draft_taxonomy(product_name: str, category: str, sample: pd.DataFrame) -> dict:
    """One Claude call, given only the real sampled reviews -- it reads them
    and proposes a bottom-up taxonomy; it does not invent categories from
    knowledge of the product. Same schema as data/taxonomy.yaml so a human
    reviewer can diff it directly against WHOOP's."""
    from evals.preflight import api_error
    problem = api_error()
    if problem:
        raise RuntimeError(f"API not usable: {problem}")

    from anthropic import Anthropic
    client = Anthropic()

    review_lines = "\n".join(
        f"[{r.sample_id}] ({r.source}, {r.rating}★) {str(r.text)[:300]}"
        for r in sample.itertuples()
    )

    prompt = f"""You are doing bottom-up open coding of real {product_name} ({category}) app reviews to
draft a customer-feedback taxonomy, the same way this project's existing WHOOP taxonomy was built:
read real reviews, find recurring themes, group them into parent categories with 2-5 subcategories
each. Do not invent categories from general knowledge of {product_name} or similar products --
every category must be grounded in reviews actually shown below, and you must cite which sample_ids
support each subcategory.

Reviews that don't fit any coherent recurring theme should NOT be force-fit -- a healthy taxonomy
leaves some reviews uncategorized (this project's reference range is roughly 10-20% landing in
Other/Ungrouped).

Respond with ONLY YAML (no markdown fencing), in exactly this schema:

version: 1
product: {product_name}
built_from: "Bottom-up open coding of a {len(sample)}-review stratified sample (onboarding agent)."
multi_label: true
categories:
  - id: snake_case_id
    name: Human Readable Name
    definition: One sentence describing what this category covers.
    watch_category: false
    subcategories:
      - id: snake_case_sub_id
        name: Human Readable Subcategory Name
        definition: One sentence.
        supporting_sample_ids: [list of sample_id ints that led you to propose this]

Real sampled reviews:
{review_lines}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("yaml"):
            text = text[4:]
    return yaml.safe_load(text)


def build_eval_seed(slug: str, sample: pd.DataFrame) -> pd.DataFrame:
    """A subset of the sample, set aside for a HUMAN to hand-label later.
    This script does not label it -- an eval set a model labels is not an
    independent check of that model."""
    seed = sample.sample(n=min(EVAL_SEED_SIZE, len(sample)), random_state=7).reset_index(drop=True)
    seed = seed.rename(columns={"sample_id": "eval_id"})
    seed["parent_category_tags"] = ""
    seed["subcategory_tags"] = ""
    seed["notes"] = ""
    out_path = PRODUCTS_DIR / slug / "eval_seed.csv"
    seed.to_csv(out_path, index=False)
    print(f"Wrote {len(seed)}-review eval seed (unlabeled) to {out_path}")
    return seed


def build_report(slug: str, product_name: str, category: str, df: pd.DataFrame, sample: pd.DataFrame, taxonomy: dict, eval_seed: pd.DataFrame) -> str:
    lines = [
        f"# Onboarding draft: {product_name}",
        "",
        "**Nothing here is live.** No file in `backend/data/` outside `products/{slug}/` was touched, "
        "and `tag_reviews.py` was not run. This is a draft for a human to review -- see the roadmap "
        "rule: agents propose via PR/issue, you approve.".replace("{slug}", slug),
        "",
        f"- Ingested: {len(df)} real reviews",
        f"- Open-coding sample: {len(sample)} reviews",
        f"- Draft taxonomy: {len(taxonomy.get('categories', []))} parent categories, "
        f"{sum(len(c.get('subcategories', [])) for c in taxonomy.get('categories', []))} subcategories",
        f"- Eval seed: {len(eval_seed)} reviews set aside, unlabeled, for hand-labeling",
        "",
        "## Draft taxonomy",
        "",
    ]
    for c in taxonomy.get("categories", []):
        lines.append(f"### {c.get('name')} (`{c.get('id')}`)")
        lines.append(c.get("definition", ""))
        for sub in c.get("subcategories", []):
            ids = sub.get("supporting_sample_ids", [])
            lines.append(f"- **{sub.get('name')}** (`{sub.get('id')}`) -- {sub.get('definition', '')} "
                         f"_(sample ids: {ids})_")
        lines.append("")
    lines += [
        "## Next steps for a human reviewer",
        "",
        f"1. Read `products/{slug}/taxonomy_draft.yaml` against the sample reviews it cites.",
        "2. Edit/merge it into a real taxonomy.yaml for this product once it looks right.",
        f"3. Hand-label `products/{slug}/eval_seed.csv` (fill in parent_category_tags/subcategory_tags) "
        "so there's an eval gate before tagging the full corpus, same as WHOOP's evals/tagger_eval.py.",
        "4. Only then run tagging on this product's full dataset.",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-name", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--slug", default=None)
    parser.add_argument("--google-play-package", default=None)
    parser.add_argument("--app-store-id", default=None)
    parser.add_argument("--country", default="us")
    parser.add_argument("--sample-size", type=int, default=150)
    args = parser.parse_args()

    if not args.google_play_package and not args.app_store_id:
        parser.error("need at least one of --google-play-package / --app-store-id")

    slug = args.slug or slugify(args.product_name)
    print(f"Onboarding '{args.product_name}' as '{slug}'...\n")

    df, _ = ingest(slug, args.google_play_package, args.app_store_id, args.country)
    if len(df) == 0:
        print("No reviews ingested -- stopping (check the package/app id and ingest_report.md).", file=sys.stderr)
        return 1

    sample = draw_sample(slug, df, args.sample_size)

    print("\nAsking Claude to draft a bottom-up taxonomy from the real sample...")
    taxonomy = draft_taxonomy(args.product_name, args.category, sample)
    taxonomy_path = PRODUCTS_DIR / slug / "taxonomy_draft.yaml"
    taxonomy_path.write_text(yaml.dump(taxonomy, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote draft taxonomy to {taxonomy_path}")

    eval_seed = build_eval_seed(slug, sample)

    report = build_report(slug, args.product_name, args.category, df, sample, taxonomy, eval_seed)
    report_path = PRODUCTS_DIR / slug / "onboarding_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nWrote {report_path}\n")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
