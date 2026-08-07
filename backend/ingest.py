"""Real-data ingestion for ActionLayer v2.

Pulls WHOOP reviews from Google Play and the Apple App Store, normalizes them
into one schema, and upserts them into data/whoop_reviews_raw.csv (+ writes
data/README.md). This is an upsert, not an overwrite: Apple's public RSS feed
only ever returns the ~500 most recent reviews, so on a repeat run reviews
that aged out of that window are carried over from the existing CSV rather
than dropped. See ingestion/merge.py for the merge semantics.

No taxonomy, tagging, or LLM calls happen here — this is ingestion only.
Every row in the output came from a live API/scrape response; nothing is
generated, inferred, or backfilled. If a source returns less than hoped for,
that real count is what gets reported.

Run with: python ingest.py
Intended to run daily (see .github/workflows/ingest.yml) so new reviews
accumulate over time instead of the dataset being frozen at whatever a single
pull happened to catch.
"""

import csv
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ingestion.app_store import fetch_app_store_reviews
from ingestion.google_play import fetch_google_play_reviews
from ingestion.merge import load_existing, merge_upsert
from ingestion.normalize import SCHEMA_FIELDS, clean_and_dedupe, normalize_app_store, normalize_google_play
from ingestion.report import build_summary, render_markdown

PRODUCT_NAME = "WHOOP"
GOOGLE_PLAY_PACKAGE = "com.whoop.android"
APP_STORE_ID = "933944389"
COUNTRY = "us"

DATA_DIR = Path(__file__).parent / "data"
CSV_PATH = DATA_DIR / "whoop_reviews_raw.csv"
README_PATH = DATA_DIR / "README.md"


def main():
    all_issues: list[str] = []

    print(f"Fetching Google Play reviews for {GOOGLE_PLAY_PACKAGE} ...")
    gp_raw, gp_issues = fetch_google_play_reviews(GOOGLE_PLAY_PACKAGE, country=COUNTRY)
    all_issues += gp_issues
    print(f"  -> {len(gp_raw)} raw reviews")

    print(f"Fetching Apple App Store reviews for id{APP_STORE_ID} ...")
    as_raw, as_issues = fetch_app_store_reviews(APP_STORE_ID, country=COUNTRY)
    all_issues += as_issues
    print(f"  -> {len(as_raw)} raw reviews")

    rows = normalize_google_play(gp_raw, COUNTRY) + normalize_app_store(as_raw, COUNTRY)
    kept_rows, drop_counts = clean_and_dedupe(rows)

    existing = load_existing(CSV_PATH)
    merged_rows, merge_counts = merge_upsert(existing, kept_rows)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_FIELDS)
        writer.writeheader()
        writer.writerows(merged_rows)
    print(
        f"Wrote {len(merged_rows)} reviews to {CSV_PATH} "
        f"({merge_counts['new']} new, {merge_counts['updated']} updated, "
        f"{merge_counts['carried_over']} carried over from a prior pull)"
    )

    summary = build_summary(PRODUCT_NAME, merged_rows, drop_counts, all_issues, merge_counts)
    report_text = render_markdown(summary)

    README_PATH.write_text(report_text, encoding="utf-8")
    print(f"Wrote summary to {README_PATH}")

    print()
    print(report_text)


if __name__ == "__main__":
    main()
