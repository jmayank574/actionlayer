# WHOOP review dataset

Generated 2026-08-17T13:41:26.843512

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 1
- Returned again, unchanged: 2865
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 526

## By source

### google_play

- Total reviews: **2870**
- Date range: 2017-08-25T20:34:31 to 2026-08-16T09:52:44
- Rating distribution: 1★: 1096 | 2★: 359 | 3★: 314 | 4★: 272 | 5★: 829
- Average review length: 37.8 words

### app_store

- Total reviews: **525**
- Date range: 2025-11-17T19:06:49 to 2026-08-15T03:18:31
- Rating distribution: 1★: 163 | 2★: 46 | 3★: 55 | 4★: 54 | 5★: 207
- Average review length: 56.1 words

## Combined

- Total reviews: **3395**
- Date range: 2017-08-25T20:34:31 to 2026-08-16T09:52:44
- Rating distribution: 1★: 1259 | 2★: 405 | 3★: 369 | 4★: 326 | 5★: 1036
- Average review length: 40.6 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 402
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: page 1 returned 0 entries (HTTP 200) -- likely a transient per-storefront throttle from Apple, not a real empty feed. No reviews collected this pull; prior data was left untouched by the upsert.
