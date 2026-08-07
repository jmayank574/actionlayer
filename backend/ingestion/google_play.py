import time

from google_play_scraper import Sort, reviews

# Safety valve against an infinite loop if the API ever returns a token that
# never resolves to None — not a target or a cap on real review volume.
MAX_BATCHES = 2000
BATCH_SIZE = 200
SLEEP_BETWEEN_CALLS = 0.3
MAX_CONSECUTIVE_ERRORS = 3


def fetch_google_play_reviews(package_name: str, lang: str = "en", country: str = "us") -> tuple[list[dict], list[str]]:
    """Pull every review the API will return for `package_name`, paginating via
    continuation_token until Google stops returning new pages. Returns
    (raw_reviews, issues) — issues is a list of human-readable strings describing
    anything that limited coverage (errors, early termination, etc.)."""
    all_reviews: list[dict] = []
    issues: list[str] = []
    token = None
    consecutive_errors = 0

    for batch_num in range(MAX_BATCHES):
        try:
            batch, token = reviews(
                package_name,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=BATCH_SIZE,
                continuation_token=token,
            )
            consecutive_errors = 0
        except Exception as e:
            consecutive_errors += 1
            issues.append(f"Google Play: request failed on batch {batch_num} ({e!r})")
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                issues.append(
                    f"Google Play: stopped after {consecutive_errors} consecutive failures — "
                    f"{len(all_reviews)} reviews collected before the pull was cut short."
                )
                break
            time.sleep(SLEEP_BETWEEN_CALLS * 2)
            continue

        if not batch:
            break

        all_reviews.extend(batch)

        if token is None:
            break

        time.sleep(SLEEP_BETWEEN_CALLS)
    else:
        issues.append(
            f"Google Play: hit the {MAX_BATCHES}-batch safety cap "
            f"({MAX_BATCHES * BATCH_SIZE} reviews) — the API may have had more to give."
        )

    return all_reviews, issues
