# WHOOP review dataset

Generated 2026-09-18T16:59:06.859104

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **6**
- Edited since last seen: 0
- Returned again, unchanged: 3361
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 204

## By source

### google_play

- Total reviews: **2924**
- Date range: 2017-08-25T20:34:31 to 2026-09-17T15:32:08
- Rating distribution: 1★: 1110 | 2★: 367 | 3★: 323 | 4★: 278 | 5★: 846
- Average review length: 37.8 words

### app_store

- Total reviews: **647**
- Date range: 2025-11-17T19:06:49 to 2026-09-16T14:33:46
- Rating distribution: 1★: 193 | 2★: 57 | 3★: 62 | 4★: 63 | 5★: 272
- Average review length: 53.7 words

## Combined

- Total reviews: **3571**
- Date range: 2017-08-25T20:34:31 to 2026-09-17T15:32:08
- Rating distribution: 1★: 1303 | 2★: 424 | 3★: 385 | 4★: 341 | 5★: 1118
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 473
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
