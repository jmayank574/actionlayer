# WHOOP review dataset

Generated 2026-08-08T01:27:51.856000

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **0**
- Edited since last seen: 0
- Returned again, unchanged: 2841
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 472

## By source

### google_play

- Total reviews: **2841**
- Date range: 2017-08-25T20:34:31 to 2026-08-06T12:43:19
- Rating distribution: 1★: 1088 | 2★: 357 | 3★: 311 | 4★: 271 | 5★: 814
- Average review length: 37.8 words

### app_store

- Total reviews: **472**
- Date range: 2025-11-17T19:06:49 to 2026-08-06T03:52:46
- Rating distribution: 1★: 151 | 2★: 43 | 3★: 47 | 4★: 49 | 5★: 182
- Average review length: 55.0 words

## Combined

- Total reviews: **3313**
- Date range: 2017-08-25T20:34:31 to 2026-08-06T12:43:19
- Rating distribution: 1★: 1239 | 2★: 400 | 3★: 358 | 4★: 320 | 5★: 996
- Average review length: 40.3 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 396
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: page 1 returned 0 entries (HTTP 200) -- likely a transient per-storefront throttle from Apple, not a real empty feed. No reviews collected this pull; prior data was left untouched by the upsert.
