# WHOOP review dataset

Generated 2026-10-15T17:40:42.558393

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **7**
- Edited since last seen: 2
- Returned again, unchanged: 3394
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 282

## By source

### google_play

- Total reviews: **2965**
- Date range: 2017-08-25T20:34:31 to 2026-10-14T15:35:31
- Rating distribution: 1★: 1119 | 2★: 374 | 3★: 330 | 4★: 281 | 5★: 861
- Average review length: 37.8 words

### app_store

- Total reviews: **720**
- Date range: 2025-11-17T19:06:49 to 2026-10-13T23:46:58
- Rating distribution: 1★: 213 | 2★: 64 | 3★: 66 | 4★: 70 | 5★: 307
- Average review length: 53.4 words

## Combined

- Total reviews: **3685**
- Date range: 2017-08-25T20:34:31 to 2026-10-14T15:35:31
- Rating distribution: 1★: 1332 | 2★: 438 | 3★: 396 | 4★: 351 | 5★: 1168
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 490
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
