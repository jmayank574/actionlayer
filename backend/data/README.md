# WHOOP review dataset

Generated 2026-11-21T19:59:16.597327

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **4**
- Edited since last seen: 1
- Returned again, unchanged: 3448
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 383

## By source

### google_play

- Total reviews: **3016**
- Date range: 2017-08-25T20:34:31 to 2026-11-20T03:56:40
- Rating distribution: 1★: 1132 | 2★: 376 | 3★: 339 | 4★: 284 | 5★: 885
- Average review length: 37.7 words

### app_store

- Total reviews: **820**
- Date range: 2025-11-17T19:06:49 to 2026-11-19T14:47:47
- Rating distribution: 1★: 239 | 2★: 73 | 3★: 75 | 4★: 80 | 5★: 353
- Average review length: 52.3 words

## Combined

- Total reviews: **3836**
- Date range: 2017-08-25T20:34:31 to 2026-11-20T03:56:40
- Rating distribution: 1★: 1371 | 2★: 449 | 3★: 414 | 4★: 364 | 5★: 1238
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 509
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
