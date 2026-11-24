# WHOOP review dataset

Generated 2026-11-24T22:57:02.682285

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **1**
- Edited since last seen: 0
- Returned again, unchanged: 3456
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 390

## By source

### google_play

- Total reviews: **3021**
- Date range: 2017-08-25T20:34:31 to 2026-11-23T18:03:41
- Rating distribution: 1★: 1132 | 2★: 377 | 3★: 341 | 4★: 284 | 5★: 887
- Average review length: 37.7 words

### app_store

- Total reviews: **826**
- Date range: 2025-11-17T19:06:49 to 2026-11-22T07:00:04
- Rating distribution: 1★: 240 | 2★: 74 | 3★: 75 | 4★: 81 | 5★: 356
- Average review length: 52.3 words

## Combined

- Total reviews: **3847**
- Date range: 2017-08-25T20:34:31 to 2026-11-23T18:03:41
- Rating distribution: 1★: 1372 | 2★: 451 | 3★: 416 | 4★: 365 | 5★: 1243
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 509
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
