# WHOOP review dataset

Generated 2026-08-19T13:47:36.637625

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **9**
- Edited since last seen: 0
- Returned again, unchanged: 3319
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 85

## By source

### google_play

- Total reviews: **2871**
- Date range: 2017-08-25T20:34:31 to 2026-08-17T13:51:27
- Rating distribution: 1★: 1096 | 2★: 360 | 3★: 314 | 4★: 272 | 5★: 829
- Average review length: 37.8 words

### app_store

- Total reviews: **542**
- Date range: 2025-11-17T19:06:49 to 2026-08-18T04:38:51
- Rating distribution: 1★: 167 | 2★: 48 | 3★: 57 | 4★: 54 | 5★: 216
- Average review length: 55.7 words

## Combined

- Total reviews: **3413**
- Date range: 2017-08-25T20:34:31 to 2026-08-18T04:38:51
- Rating distribution: 1★: 1263 | 2★: 408 | 3★: 371 | 4★: 326 | 5★: 1045
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 445
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
