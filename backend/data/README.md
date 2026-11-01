# WHOOP review dataset

Generated 2026-11-01T18:18:15.251338

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **0**
- Edited since last seen: 0
- Returned again, unchanged: 2978
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 770

## By source

### google_play

- Total reviews: **2986**
- Date range: 2017-08-25T20:34:31 to 2026-10-30T12:41:26
- Rating distribution: 1★: 1127 | 2★: 374 | 3★: 332 | 4★: 281 | 5★: 872
- Average review length: 37.8 words

### app_store

- Total reviews: **762**
- Date range: 2025-11-17T19:06:49 to 2026-10-30T04:39:13
- Rating distribution: 1★: 222 | 2★: 66 | 3★: 69 | 4★: 78 | 5★: 327
- Average review length: 52.6 words

## Combined

- Total reviews: **3748**
- Date range: 2017-08-25T20:34:31 to 2026-10-30T12:41:26
- Rating distribution: 1★: 1349 | 2★: 440 | 3★: 401 | 4★: 359 | 5★: 1199
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 444
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: page 1 returned 0 entries (HTTP 200) -- likely a transient per-storefront throttle from Apple, not a real empty feed. No reviews collected this pull; prior data was left untouched by the upsert.
