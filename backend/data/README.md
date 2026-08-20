# WHOOP review dataset

Generated 2026-08-20T13:50:25.681941

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **6**
- Edited since last seen: 0
- Returned again, unchanged: 3323
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 90

## By source

### google_play

- Total reviews: **2873**
- Date range: 2017-08-25T20:34:31 to 2026-08-18T17:09:14
- Rating distribution: 1★: 1096 | 2★: 360 | 3★: 314 | 4★: 272 | 5★: 831
- Average review length: 37.8 words

### app_store

- Total reviews: **546**
- Date range: 2025-11-17T19:06:49 to 2026-08-18T21:09:12
- Rating distribution: 1★: 168 | 2★: 48 | 3★: 57 | 4★: 55 | 5★: 218
- Average review length: 56.1 words

## Combined

- Total reviews: **3419**
- Date range: 2017-08-25T20:34:31 to 2026-08-18T21:09:12
- Rating distribution: 1★: 1264 | 2★: 408 | 3★: 371 | 4★: 327 | 5★: 1049
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 446
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
