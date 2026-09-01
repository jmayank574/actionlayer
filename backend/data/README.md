# WHOOP review dataset

Generated 2026-09-01T17:13:56.196124

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **12**
- Edited since last seen: 1
- Returned again, unchanged: 3331
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 131

## By source

### google_play

- Total reviews: **2891**
- Date range: 2017-08-25T20:34:31 to 2026-08-31T14:55:31
- Rating distribution: 1★: 1098 | 2★: 363 | 3★: 319 | 4★: 275 | 5★: 836
- Average review length: 37.8 words

### app_store

- Total reviews: **584**
- Date range: 2025-11-17T19:06:49 to 2026-08-31T04:45:37
- Rating distribution: 1★: 178 | 2★: 50 | 3★: 58 | 4★: 57 | 5★: 241
- Average review length: 55.0 words

## Combined

- Total reviews: **3475**
- Date range: 2017-08-25T20:34:31 to 2026-08-31T14:55:31
- Rating distribution: 1★: 1276 | 2★: 413 | 3★: 377 | 4★: 332 | 5★: 1077
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 455
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
