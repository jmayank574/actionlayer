# WHOOP review dataset

Generated 2026-09-23T17:45:52.706748

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 0
- Returned again, unchanged: 2926
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 662

## By source

### google_play

- Total reviews: **2936**
- Date range: 2017-08-25T20:34:31 to 2026-09-22T17:38:33
- Rating distribution: 1★: 1111 | 2★: 369 | 3★: 326 | 4★: 280 | 5★: 850
- Average review length: 37.8 words

### app_store

- Total reviews: **655**
- Date range: 2025-11-17T19:06:49 to 2026-09-19T05:52:13
- Rating distribution: 1★: 193 | 2★: 58 | 3★: 62 | 4★: 66 | 5★: 276
- Average review length: 53.8 words

## Combined

- Total reviews: **3591**
- Date range: 2017-08-25T20:34:31 to 2026-09-22T17:38:33
- Rating distribution: 1★: 1304 | 2★: 427 | 3★: 388 | 4★: 346 | 5★: 1126
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 422
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: page 1 returned 0 entries (HTTP 200) -- likely a transient per-storefront throttle from Apple, not a real empty feed. No reviews collected this pull; prior data was left untouched by the upsert.
