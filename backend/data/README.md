# WHOOP review dataset

Generated 2026-08-23T13:34:54.792319

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 2
- Returned again, unchanged: 3327
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 104

## By source

### google_play

- Total reviews: **2881**
- Date range: 2017-08-25T20:34:31 to 2026-08-22T06:15:43
- Rating distribution: 1★: 1098 | 2★: 360 | 3★: 316 | 4★: 273 | 5★: 834
- Average review length: 37.8 words

### app_store

- Total reviews: **557**
- Date range: 2025-11-17T19:06:49 to 2026-08-21T17:57:13
- Rating distribution: 1★: 171 | 2★: 49 | 3★: 57 | 4★: 54 | 5★: 226
- Average review length: 55.7 words

## Combined

- Total reviews: **3438**
- Date range: 2017-08-25T20:34:31 to 2026-08-22T06:15:43
- Rating distribution: 1★: 1269 | 2★: 409 | 3★: 373 | 4★: 327 | 5★: 1060
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 451
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
