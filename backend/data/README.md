# WHOOP review dataset

Generated 2026-08-11T01:52:55.923459

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **0**
- Edited since last seen: 0
- Returned again, unchanged: 3305
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 43

## By source

### google_play

- Total reviews: **2850**
- Date range: 2017-08-25T20:34:31 to 2026-08-09T16:08:56
- Rating distribution: 1★: 1092 | 2★: 357 | 3★: 312 | 4★: 271 | 5★: 818
- Average review length: 37.8 words

### app_store

- Total reviews: **498**
- Date range: 2025-11-17T19:06:49 to 2026-08-09T07:31:46
- Rating distribution: 1★: 157 | 2★: 44 | 3★: 51 | 4★: 50 | 5★: 196
- Average review length: 54.8 words

## Combined

- Total reviews: **3348**
- Date range: 2017-08-25T20:34:31 to 2026-08-09T16:08:56
- Rating distribution: 1★: 1249 | 2★: 401 | 3★: 363 | 4★: 321 | 5★: 1014
- Average review length: 40.3 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 441
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
