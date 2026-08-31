# WHOOP review dataset

Generated 2026-08-31T19:27:01.022672

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **1**
- Edited since last seen: 0
- Returned again, unchanged: 2885
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 577

## By source

### google_play

- Total reviews: **2889**
- Date range: 2017-08-25T20:34:31 to 2026-08-30T05:39:43
- Rating distribution: 1★: 1098 | 2★: 363 | 3★: 317 | 4★: 275 | 5★: 836
- Average review length: 37.8 words

### app_store

- Total reviews: **574**
- Date range: 2025-11-17T19:06:49 to 2026-08-27T05:40:03
- Rating distribution: 1★: 176 | 2★: 49 | 3★: 58 | 4★: 56 | 5★: 235
- Average review length: 55.0 words

## Combined

- Total reviews: **3463**
- Date range: 2017-08-25T20:34:31 to 2026-08-30T05:39:43
- Rating distribution: 1★: 1274 | 2★: 412 | 3★: 375 | 4★: 331 | 5★: 1071
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 410
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: page 1 returned 0 entries (HTTP 200) -- likely a transient per-storefront throttle from Apple, not a real empty feed. No reviews collected this pull; prior data was left untouched by the upsert.
