# WHOOP review dataset

Generated 2026-08-12T14:21:55.809666

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **10**
- Edited since last seen: 0
- Returned again, unchanged: 3299
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 50

## By source

### google_play

- Total reviews: **2854**
- Date range: 2017-08-25T20:34:31 to 2026-08-11T07:17:04
- Rating distribution: 1★: 1093 | 2★: 357 | 3★: 312 | 4★: 272 | 5★: 820
- Average review length: 37.8 words

### app_store

- Total reviews: **505**
- Date range: 2025-11-17T19:06:49 to 2026-08-10T21:41:50
- Rating distribution: 1★: 158 | 2★: 44 | 3★: 51 | 4★: 53 | 5★: 199
- Average review length: 54.6 words

## Combined

- Total reviews: **3359**
- Date range: 2017-08-25T20:34:31 to 2026-08-11T07:17:04
- Rating distribution: 1★: 1251 | 2★: 401 | 3★: 363 | 4★: 325 | 5★: 1019
- Average review length: 40.3 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 441
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
