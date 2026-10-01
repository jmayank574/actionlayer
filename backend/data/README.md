# WHOOP review dataset

Generated 2026-10-01T18:44:31.848760

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **6**
- Edited since last seen: 1
- Returned again, unchanged: 3382
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 236

## By source

### google_play

- Total reviews: **2949**
- Date range: 2017-08-25T20:34:31 to 2026-09-30T13:16:34
- Rating distribution: 1★: 1114 | 2★: 370 | 3★: 328 | 4★: 280 | 5★: 857
- Average review length: 37.8 words

### app_store

- Total reviews: **676**
- Date range: 2025-11-17T19:06:49 to 2026-09-30T02:02:26
- Rating distribution: 1★: 201 | 2★: 60 | 3★: 63 | 4★: 67 | 5★: 285
- Average review length: 54.0 words

## Combined

- Total reviews: **3625**
- Date range: 2017-08-25T20:34:31 to 2026-09-30T13:16:34
- Rating distribution: 1★: 1315 | 2★: 430 | 3★: 391 | 4★: 347 | 5★: 1142
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 481
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
