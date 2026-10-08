# WHOOP review dataset

Generated 2026-10-08T19:11:50.021677

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 0
- Returned again, unchanged: 3388
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 258

## By source

### google_play

- Total reviews: **2954**
- Date range: 2017-08-25T20:34:31 to 2026-10-07T10:54:37
- Rating distribution: 1★: 1116 | 2★: 370 | 3★: 329 | 4★: 281 | 5★: 858
- Average review length: 37.8 words

### app_store

- Total reviews: **697**
- Date range: 2025-11-17T19:06:49 to 2026-10-06T15:20:54
- Rating distribution: 1★: 206 | 2★: 61 | 3★: 64 | 4★: 69 | 5★: 297
- Average review length: 54.0 words

## Combined

- Total reviews: **3651**
- Date range: 2017-08-25T20:34:31 to 2026-10-07T10:54:37
- Rating distribution: 1★: 1322 | 2★: 431 | 3★: 393 | 4★: 350 | 5★: 1155
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 486
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
