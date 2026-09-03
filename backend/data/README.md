# WHOOP review dataset

Generated 2026-09-03T16:58:26.954054

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **10**
- Edited since last seen: 0
- Returned again, unchanged: 3336
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 141

## By source

### google_play

- Total reviews: **2895**
- Date range: 2017-08-25T20:34:31 to 2026-09-02T15:27:46
- Rating distribution: 1★: 1099 | 2★: 363 | 3★: 319 | 4★: 276 | 5★: 838
- Average review length: 37.8 words

### app_store

- Total reviews: **592**
- Date range: 2025-11-17T19:06:49 to 2026-09-02T05:13:37
- Rating distribution: 1★: 180 | 2★: 51 | 3★: 58 | 4★: 57 | 5★: 246
- Average review length: 54.9 words

## Combined

- Total reviews: **3487**
- Date range: 2017-08-25T20:34:31 to 2026-09-02T15:27:46
- Rating distribution: 1★: 1279 | 2★: 414 | 3★: 377 | 4★: 333 | 5★: 1084
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 459
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
