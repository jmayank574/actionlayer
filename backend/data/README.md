# WHOOP review dataset

Generated 2026-08-10T14:21:17.875835

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **16**
- Edited since last seen: 1
- Returned again, unchanged: 3285
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 39

## By source

### google_play

- Total reviews: **2848**
- Date range: 2017-08-25T20:34:31 to 2026-08-09T08:35:42
- Rating distribution: 1★: 1092 | 2★: 357 | 3★: 312 | 4★: 271 | 5★: 816
- Average review length: 37.8 words

### app_store

- Total reviews: **493**
- Date range: 2025-11-17T19:06:49 to 2026-08-09T04:23:44
- Rating distribution: 1★: 156 | 2★: 44 | 3★: 51 | 4★: 49 | 5★: 193
- Average review length: 54.8 words

## Combined

- Total reviews: **3341**
- Date range: 2017-08-25T20:34:31 to 2026-08-09T08:35:42
- Rating distribution: 1★: 1248 | 2★: 401 | 3★: 363 | 4★: 320 | 5★: 1009
- Average review length: 40.3 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 442
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
