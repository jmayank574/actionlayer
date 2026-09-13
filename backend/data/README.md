# WHOOP review dataset

Generated 2026-09-13T16:53:37.097207

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **10**
- Edited since last seen: 0
- Returned again, unchanged: 3350
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 191

## By source

### google_play

- Total reviews: **2915**
- Date range: 2017-08-25T20:34:31 to 2026-09-12T16:09:04
- Rating distribution: 1★: 1107 | 2★: 366 | 3★: 322 | 4★: 277 | 5★: 843
- Average review length: 37.8 words

### app_store

- Total reviews: **636**
- Date range: 2025-11-17T19:06:49 to 2026-09-12T04:41:55
- Rating distribution: 1★: 190 | 2★: 55 | 3★: 64 | 4★: 61 | 5★: 266
- Average review length: 53.8 words

## Combined

- Total reviews: **3551**
- Date range: 2017-08-25T20:34:31 to 2026-09-12T16:09:04
- Rating distribution: 1★: 1297 | 2★: 421 | 3★: 386 | 4★: 338 | 5★: 1109
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 469
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
