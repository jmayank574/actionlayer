# WHOOP review dataset

Generated 2026-08-21T13:49:18.217002

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **9**
- Edited since last seen: 0
- Returned again, unchanged: 3324
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 95

## By source

### google_play

- Total reviews: **2877**
- Date range: 2017-08-25T20:34:31 to 2026-08-20T10:40:34
- Rating distribution: 1★: 1098 | 2★: 360 | 3★: 315 | 4★: 272 | 5★: 832
- Average review length: 37.8 words

### app_store

- Total reviews: **551**
- Date range: 2025-11-17T19:06:49 to 2026-08-19T21:33:08
- Rating distribution: 1★: 170 | 2★: 48 | 3★: 57 | 4★: 55 | 5★: 221
- Average review length: 56.0 words

## Combined

- Total reviews: **3428**
- Date range: 2017-08-25T20:34:31 to 2026-08-20T10:40:34
- Rating distribution: 1★: 1268 | 2★: 408 | 3★: 372 | 4★: 327 | 5★: 1053
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 446
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
