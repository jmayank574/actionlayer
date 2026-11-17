# WHOOP review dataset

Generated 2026-11-17T21:34:29.093841

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **7**
- Edited since last seen: 0
- Returned again, unchanged: 3435
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 369

## By source

### google_play

- Total reviews: **3007**
- Date range: 2017-08-25T20:34:31 to 2026-11-16T21:22:34
- Rating distribution: 1★: 1132 | 2★: 376 | 3★: 334 | 4★: 284 | 5★: 881
- Average review length: 37.7 words

### app_store

- Total reviews: **804**
- Date range: 2025-11-17T19:06:49 to 2026-11-15T23:46:06
- Rating distribution: 1★: 232 | 2★: 71 | 3★: 73 | 4★: 81 | 5★: 347
- Average review length: 52.9 words

## Combined

- Total reviews: **3811**
- Date range: 2017-08-25T20:34:31 to 2026-11-16T21:22:34
- Rating distribution: 1★: 1364 | 2★: 447 | 3★: 407 | 4★: 365 | 5★: 1228
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 510
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
