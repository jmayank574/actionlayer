from datetime import timezone

MIN_WORD_COUNT = 5

# first_seen_at/last_seen_at are set by ingestion/merge.py during the upsert
# step, not here -- normalize_* only shapes what each source's API returned.
SCHEMA_FIELDS = [
    "source", "review_id", "rating", "date", "text", "app_version", "country",
    "first_seen_at", "last_seen_at",
]


def _google_play_date_to_utc_iso(at) -> str | None:
    """google_play_scraper returns a naive datetime that's actually local
    wall-clock time on whatever machine made the request (confirmed
    empirically: same review, 7h apart between a Pacific dev machine and a
    UTC CI runner). datetime.astimezone() on a naive value is documented to
    assume system-local time and convert correctly from there -- without
    this, every review's date silently shifts depending on which machine
    last ingested it, and merge.py's "did this change?" check flags nearly
    the entire corpus as edited every time ingestion alternates machines."""
    if not hasattr(at, "isoformat"):
        return str(at) if at else None
    return at.astimezone(timezone.utc).isoformat()


def normalize_google_play(raw_reviews: list[dict], country: str) -> list[dict]:
    rows = []
    for r in raw_reviews:
        at = r.get("at")
        rows.append({
            "source": "google_play",
            "review_id": r.get("reviewId"),
            "rating": r.get("score"),
            "date": _google_play_date_to_utc_iso(at),
            "text": (r.get("content") or "").strip(),
            "app_version": r.get("appVersion") or r.get("reviewCreatedVersion") or None,
            "country": country,
        })
    return rows


def normalize_app_store(raw_entries: list[dict], country: str) -> list[dict]:
    rows = []
    for e in raw_entries:
        rows.append({
            "source": "app_store",
            "review_id": (e.get("id") or {}).get("label"),
            "rating": _to_int((e.get("im:rating") or {}).get("label")),
            "date": (e.get("updated") or {}).get("label"),
            "text": ((e.get("content") or {}).get("label") or "").strip(),
            "app_version": (e.get("im:version") or {}).get("label"),
            "country": country,
        })
    return rows


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def clean_and_dedupe(rows: list[dict]) -> tuple[list[dict], dict]:
    """Drop empty/near-empty reviews and exact (review_id, text) duplicates.
    Never filters on rating, sentiment, or topic. Returns (kept_rows, drop_counts)."""
    dropped_empty = 0
    seen: set[tuple] = set()
    dropped_duplicate = 0
    kept: list[dict] = []

    for row in rows:
        text = row.get("text") or ""
        word_count = len(text.split())
        if word_count < MIN_WORD_COUNT:
            dropped_empty += 1
            continue

        key = (row.get("review_id"), text)
        if key in seen:
            dropped_duplicate += 1
            continue
        seen.add(key)
        kept.append(row)

    return kept, {"dropped_empty_or_short": dropped_empty, "dropped_duplicate": dropped_duplicate}
