# WHOOP review dataset

Generated 2026-10-23T17:46:52.765475

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **6**
- Edited since last seen: 0
- Returned again, unchanged: 3404
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 309

## By source

### google_play

- Total reviews: **2973**
- Date range: 2017-08-25T20:34:31 to 2026-10-22T14:07:33
- Rating distribution: 1★: 1123 | 2★: 374 | 3★: 330 | 4★: 281 | 5★: 865
- Average review length: 37.8 words

### app_store

- Total reviews: **746**
- Date range: 2025-11-17T19:06:49 to 2026-10-22T04:14:35
- Rating distribution: 1★: 215 | 2★: 63 | 3★: 69 | 4★: 75 | 5★: 324
- Average review length: 52.8 words

## Combined

- Total reviews: **3719**
- Date range: 2017-08-25T20:34:31 to 2026-10-22T14:07:33
- Rating distribution: 1★: 1338 | 2★: 437 | 3★: 399 | 4★: 356 | 5★: 1189
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 492
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
