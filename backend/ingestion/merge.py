"""Upsert layer between a fresh ingestion pull and the persisted raw CSV.

Google Play's API returns the full review history on every pull, so it never
needed this. Apple's public RSS feed caps out at ~500 most-recent reviews
(see ingestion/app_store.py) -- run ingest.py again in a week and reviews
older than that window are simply gone from the response. Overwriting the CSV
with each pull's output would silently delete them. Upserting keeps every
review ever captured: new reviews are added, previously-seen reviews are
refreshed in place (a user can edit their review after posting), and reviews
this pull didn't return are carried over untouched.
"""

import csv
from datetime import datetime, timezone
from pathlib import Path

CONTENT_FIELDS = ("rating", "date", "text", "app_version")


def load_existing(csv_path: Path) -> dict[tuple, dict]:
    """Load a previously-written raw CSV into {(source, review_id): row}.
    Returns an empty dict on the first-ever run, when no file exists yet."""
    if not csv_path.exists():
        return {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        result = {}
        for row in reader:
            # csv.DictReader hands back strings for everything -- reparse rating
            # to int so carried-over rows (untouched by this pull) match the
            # type normalize.py gives freshly-fetched rows. Otherwise a report
            # stat like rating_distribution silently drops every carried-over
            # row because int(4) != "4".
            raw_rating = row.get("rating")
            try:
                row["rating"] = int(raw_rating) if raw_rating not in (None, "") else None
            except ValueError:
                row["rating"] = None
            # csv.DictWriter turns a None app_version into '' on write; reparse
            # it back to None here too, or every carried-over row with no
            # version gets misdetected as "updated" against a fresh None.
            if row.get("app_version") == "":
                row["app_version"] = None
            result[(row["source"], row["review_id"])] = row
        return result


def merge_upsert(existing: dict[tuple, dict], fresh_rows: list[dict]) -> tuple[list[dict], dict]:
    """Merge freshly-fetched rows into the existing set. Returns (merged_rows, counts).

    counts = {"new": ..., "updated": ..., "unchanged": ..., "carried_over": ...}
    - new: reviews never seen before
    - updated: previously-seen reviews whose content changed (edited by the author)
    - unchanged: previously-seen reviews returned again with identical content
    - carried_over: previously-seen reviews this pull didn't return at all
      (e.g. aged out of Apple's RSS window) -- kept as-is, not dropped
    """
    now = datetime.now(timezone.utc).isoformat()
    merged = dict(existing)
    new_count = 0
    updated_count = 0
    unchanged_count = 0

    for row in fresh_rows:
        key = (row["source"], row["review_id"])
        prior = merged.get(key)
        if prior is None:
            row["first_seen_at"] = now
            row["last_seen_at"] = now
            merged[key] = row
            new_count += 1
        else:
            changed = any(str(prior.get(f, "")) != str(row.get(f, "")) for f in CONTENT_FIELDS)
            row["first_seen_at"] = prior.get("first_seen_at") or now
            row["last_seen_at"] = now if changed else prior.get("last_seen_at", now)
            merged[key] = row
            if changed:
                updated_count += 1
            else:
                unchanged_count += 1

    carried_over = len(existing) - (updated_count + unchanged_count)
    counts = {
        "new": new_count,
        "updated": updated_count,
        "unchanged": unchanged_count,
        "carried_over": carried_over,
    }
    return list(merged.values()), counts
