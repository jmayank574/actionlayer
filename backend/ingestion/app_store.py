import time

import requests

# Apple's public customer-reviews RSS feed is capped by Apple at 10 pages of
# 50 reviews each (~500 most-recent reviews) — this is a real, documented
# limit of the endpoint itself, not a choice made here.
MAX_PAGES = 10
SLEEP_BETWEEN_CALLS = 0.3

# app-store-scraper's review() method depends on scraping a bearer token out
# of a <meta ... web-experience-app/config/environment> tag on the App Store
# landing page. That tag no longer exists in Apple's current markup (verified
# 2026-08-04 — every request came back 401), so it can't authenticate at all.
# Apple's own public RSS feed is used instead: same underlying real data,
# no third-party dependency required.
RSS_URL_TEMPLATE = (
    "https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/"
    "sortby=mostrecent/page={page}/json"
)


def fetch_app_store_reviews(app_id: str, country: str = "us") -> tuple[list[dict], list[str]]:
    """Pull reviews from Apple's public customer-reviews RSS feed, paging until
    Apple's own cap is hit or a page fails. Returns (raw_entries, issues)."""
    all_entries: list[dict] = []
    issues: list[str] = []

    for page in range(1, MAX_PAGES + 1):
        url = RSS_URL_TEMPLATE.format(country=country, app_id=app_id, page=page)
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        except requests.RequestException as e:
            issues.append(f"App Store: request failed on page {page} ({e!r})")
            break

        if resp.status_code != 200:
            issues.append(
                f"App Store: page {page} returned HTTP {resp.status_code} — "
                f"stopping pagination there ({len(all_entries)} reviews collected)."
            )
            break

        try:
            data = resp.json()
        except ValueError:
            issues.append(
                f"App Store: page {page} did not return valid JSON — "
                f"stopping pagination there ({len(all_entries)} reviews collected)."
            )
            break

        entries = data.get("feed", {}).get("entry", [])
        if not entries:
            if page == 1:
                # A live, actively-reviewed app returning zero entries on page 1
                # (HTTP 200, valid JSON) is not "no reviews" -- it's almost
                # always a transient storefront-level throttle from Apple.
                # Flag it explicitly rather than silently reporting an empty
                # pull as if the feed were naturally exhausted.
                issues.append(
                    f"App Store: page 1 returned 0 entries (HTTP 200) -- likely a transient "
                    f"per-storefront throttle from Apple, not a real empty feed. No reviews "
                    f"collected this pull; prior data was left untouched by the upsert."
                )
            break

        all_entries.extend(entries)
        time.sleep(SLEEP_BETWEEN_CALLS)
    else:
        issues.append(
            f"App Store: hit Apple's {MAX_PAGES}-page RSS cap (~{MAX_PAGES * 50} reviews) — "
            f"this is a limit of Apple's public feed, not a failure of the pull. "
            f"Apple does not expose full review history through any public endpoint."
        )

    return all_entries, issues
