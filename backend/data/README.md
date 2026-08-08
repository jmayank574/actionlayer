# WHOOP review dataset

Generated 2026-08-08T13:49:02.481693

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 0
- Returned again, unchanged: 3294
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 19

## By source

### google_play

- Total reviews: **2841**
- Date range: 2017-08-25T20:34:31 to 2026-08-06T12:43:19
- Rating distribution: 1★: 1088 | 2★: 357 | 3★: 311 | 4★: 271 | 5★: 814
- Average review length: 37.8 words

### app_store

- Total reviews: **475**
- Date range: 2025-11-17T19:06:49 to 2026-08-07T02:01:26
- Rating distribution: 1★: 152 | 2★: 44 | 3★: 48 | 4★: 49 | 5★: 182
- Average review length: 55.3 words

## Combined

- Total reviews: **3316**
- Date range: 2017-08-25T20:34:31 to 2026-08-07T02:01:26
- Rating distribution: 1★: 1240 | 2★: 401 | 3★: 359 | 4★: 320 | 5★: 996
- Average review length: 40.3 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 440
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
