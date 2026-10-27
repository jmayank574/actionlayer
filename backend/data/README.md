# WHOOP review dataset

Generated 2026-10-27T18:36:18.552360

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **2**
- Edited since last seen: 0
- Returned again, unchanged: 3408
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 321

## By source

### google_play

- Total reviews: **2977**
- Date range: 2017-08-25T20:34:31 to 2026-10-26T03:12:20
- Rating distribution: 1★: 1123 | 2★: 375 | 3★: 330 | 4★: 281 | 5★: 868
- Average review length: 37.8 words

### app_store

- Total reviews: **754**
- Date range: 2025-11-17T19:06:49 to 2026-10-25T19:19:18
- Rating distribution: 1★: 218 | 2★: 64 | 3★: 69 | 4★: 77 | 5★: 326
- Average review length: 52.6 words

## Combined

- Total reviews: **3731**
- Date range: 2017-08-25T20:34:31 to 2026-10-26T03:12:20
- Rating distribution: 1★: 1341 | 2★: 439 | 3★: 399 | 4★: 358 | 5★: 1194
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 498
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
