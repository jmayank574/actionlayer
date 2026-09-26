# WHOOP review dataset

Generated 2026-09-26T16:57:42.674502

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 1
- Returned again, unchanged: 3373
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 229

## By source

### google_play

- Total reviews: **2941**
- Date range: 2017-08-25T20:34:31 to 2026-09-25T15:20:47
- Rating distribution: 1★: 1113 | 2★: 370 | 3★: 326 | 4★: 280 | 5★: 852
- Average review length: 37.8 words

### app_store

- Total reviews: **667**
- Date range: 2025-11-17T19:06:49 to 2026-09-25T03:45:50
- Rating distribution: 1★: 197 | 2★: 60 | 3★: 62 | 4★: 66 | 5★: 282
- Average review length: 53.7 words

## Combined

- Total reviews: **3608**
- Date range: 2017-08-25T20:34:31 to 2026-09-25T15:20:47
- Rating distribution: 1★: 1310 | 2★: 430 | 3★: 388 | 4★: 346 | 5★: 1134
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 480
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
