# WHOOP review dataset

Generated 2026-09-21T18:33:10.068562

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **2**
- Edited since last seen: 2
- Returned again, unchanged: 3366
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 215

## By source

### google_play

- Total reviews: **2930**
- Date range: 2017-08-25T20:34:31 to 2026-09-20T17:10:16
- Rating distribution: 1★: 1111 | 2★: 368 | 3★: 324 | 4★: 279 | 5★: 848
- Average review length: 37.8 words

### app_store

- Total reviews: **655**
- Date range: 2025-11-17T19:06:49 to 2026-09-19T05:52:13
- Rating distribution: 1★: 193 | 2★: 58 | 3★: 62 | 4★: 66 | 5★: 276
- Average review length: 53.8 words

## Combined

- Total reviews: **3585**
- Date range: 2017-08-25T20:34:31 to 2026-09-20T17:10:16
- Rating distribution: 1★: 1304 | 2★: 426 | 3★: 386 | 4★: 345 | 5★: 1124
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 476
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
