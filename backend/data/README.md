# WHOOP review dataset

Generated 2026-11-03T19:59:45.544065

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **4**
- Edited since last seen: 2
- Returned again, unchanged: 3418
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 335

## By source

### google_play

- Total reviews: **2988**
- Date range: 2017-08-25T20:34:31 to 2026-11-02T14:33:13
- Rating distribution: 1★: 1127 | 2★: 374 | 3★: 332 | 4★: 281 | 5★: 874
- Average review length: 37.7 words

### app_store

- Total reviews: **771**
- Date range: 2025-11-17T19:06:49 to 2026-11-01T23:07:48
- Rating distribution: 1★: 226 | 2★: 67 | 3★: 68 | 4★: 81 | 5★: 329
- Average review length: 52.7 words

## Combined

- Total reviews: **3759**
- Date range: 2017-08-25T20:34:31 to 2026-11-02T14:33:13
- Rating distribution: 1★: 1353 | 2★: 441 | 3★: 400 | 4★: 362 | 5★: 1203
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 500
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
