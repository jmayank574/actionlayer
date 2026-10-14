# WHOOP review dataset

Generated 2026-10-14T17:50:52.566012

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **7**
- Edited since last seen: 1
- Returned again, unchanged: 3390
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 280

## By source

### google_play

- Total reviews: **2961**
- Date range: 2017-08-25T20:34:31 to 2026-10-13T13:21:29
- Rating distribution: 1★: 1117 | 2★: 373 | 3★: 329 | 4★: 281 | 5★: 861
- Average review length: 37.8 words

### app_store

- Total reviews: **717**
- Date range: 2025-11-17T19:06:49 to 2026-10-13T06:03:11
- Rating distribution: 1★: 211 | 2★: 64 | 3★: 66 | 4★: 71 | 5★: 305
- Average review length: 53.4 words

## Combined

- Total reviews: **3678**
- Date range: 2017-08-25T20:34:31 to 2026-10-13T13:21:29
- Rating distribution: 1★: 1328 | 2★: 437 | 3★: 395 | 4★: 352 | 5★: 1166
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 490
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
