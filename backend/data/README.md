# WHOOP review dataset

Generated 2026-11-15T19:17:37.935762

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 1
- Returned again, unchanged: 3435
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 362

## By source

### google_play

- Total reviews: **3004**
- Date range: 2017-08-25T20:34:31 to 2026-11-14T01:01:23
- Rating distribution: 1★: 1131 | 2★: 375 | 3★: 334 | 4★: 284 | 5★: 880
- Average review length: 37.7 words

### app_store

- Total reviews: **797**
- Date range: 2025-11-17T19:06:49 to 2026-11-13T06:24:47
- Rating distribution: 1★: 232 | 2★: 71 | 3★: 72 | 4★: 81 | 5★: 341
- Average review length: 53.0 words

## Combined

- Total reviews: **3801**
- Date range: 2017-08-25T20:34:31 to 2026-11-14T01:01:23
- Rating distribution: 1★: 1363 | 2★: 446 | 3★: 406 | 4★: 365 | 5★: 1221
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 509
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
