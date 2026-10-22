# WHOOP review dataset

Generated 2026-10-22T17:53:29.618418

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **0**
- Edited since last seen: 1
- Returned again, unchanged: 3407
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 305

## By source

### google_play

- Total reviews: **2969**
- Date range: 2017-08-25T20:34:31 to 2026-10-20T10:08:03
- Rating distribution: 1★: 1121 | 2★: 373 | 3★: 330 | 4★: 281 | 5★: 864
- Average review length: 37.8 words

### app_store

- Total reviews: **744**
- Date range: 2025-11-17T19:06:49 to 2026-10-20T07:39:32
- Rating distribution: 1★: 215 | 2★: 63 | 3★: 68 | 4★: 75 | 5★: 323
- Average review length: 52.8 words

## Combined

- Total reviews: **3713**
- Date range: 2017-08-25T20:34:31 to 2026-10-20T10:08:03
- Rating distribution: 1★: 1336 | 2★: 436 | 3★: 398 | 4★: 356 | 5★: 1187
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 490
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
