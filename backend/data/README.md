# WHOOP review dataset

Generated 2026-09-28T20:02:35.509435

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **7**
- Edited since last seen: 0
- Returned again, unchanged: 3375
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 234

## By source

### google_play

- Total reviews: **2944**
- Date range: 2017-08-25T20:34:31 to 2026-09-26T22:42:39
- Rating distribution: 1★: 1113 | 2★: 371 | 3★: 326 | 4★: 280 | 5★: 854
- Average review length: 37.8 words

### app_store

- Total reviews: **672**
- Date range: 2025-11-17T19:06:49 to 2026-09-27T05:40:31
- Rating distribution: 1★: 199 | 2★: 60 | 3★: 63 | 4★: 66 | 5★: 284
- Average review length: 53.9 words

## Combined

- Total reviews: **3616**
- Date range: 2017-08-25T20:34:31 to 2026-09-27T05:40:31
- Rating distribution: 1★: 1312 | 2★: 431 | 3★: 389 | 4★: 346 | 5★: 1138
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 482
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
