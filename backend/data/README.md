# WHOOP review dataset

Generated 2026-11-16T22:46:52.159975

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 1
- Returned again, unchanged: 3436
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 364

## By source

### google_play

- Total reviews: **3005**
- Date range: 2017-08-25T20:34:31 to 2026-11-14T23:39:33
- Rating distribution: 1★: 1131 | 2★: 375 | 3★: 334 | 4★: 284 | 5★: 881
- Average review length: 37.7 words

### app_store

- Total reviews: **799**
- Date range: 2025-11-17T19:06:49 to 2026-11-14T07:57:34
- Rating distribution: 1★: 232 | 2★: 71 | 3★: 72 | 4★: 81 | 5★: 343
- Average review length: 52.9 words

## Combined

- Total reviews: **3804**
- Date range: 2017-08-25T20:34:31 to 2026-11-14T23:39:33
- Rating distribution: 1★: 1363 | 2★: 446 | 3★: 406 | 4★: 365 | 5★: 1224
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 510
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
