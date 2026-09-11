# WHOOP review dataset

Generated 2026-09-11T16:57:20.020338

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **6**
- Edited since last seen: 1
- Returned again, unchanged: 3348
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 184

## By source

### google_play

- Total reviews: **2910**
- Date range: 2017-08-25T20:34:31 to 2026-09-10T10:59:50
- Rating distribution: 1★: 1105 | 2★: 365 | 3★: 322 | 4★: 277 | 5★: 841
- Average review length: 37.8 words

### app_store

- Total reviews: **629**
- Date range: 2025-11-17T19:06:49 to 2026-09-10T05:30:24
- Rating distribution: 1★: 189 | 2★: 55 | 3★: 63 | 4★: 62 | 5★: 260
- Average review length: 54.1 words

## Combined

- Total reviews: **3539**
- Date range: 2017-08-25T20:34:31 to 2026-09-10T10:59:50
- Rating distribution: 1★: 1294 | 2★: 420 | 3★: 385 | 4★: 339 | 5★: 1101
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 467
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
