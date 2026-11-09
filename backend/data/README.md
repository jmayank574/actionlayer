# WHOOP review dataset

Generated 2026-11-09T22:54:58.085086

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **9**
- Edited since last seen: 0
- Returned again, unchanged: 3425
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 348

## By source

### google_play

- Total reviews: **2998**
- Date range: 2017-08-25T20:34:31 to 2026-11-08T16:11:27
- Rating distribution: 1★: 1128 | 2★: 375 | 3★: 334 | 4★: 282 | 5★: 879
- Average review length: 37.7 words

### app_store

- Total reviews: **784**
- Date range: 2025-11-17T19:06:49 to 2026-11-08T09:02:25
- Rating distribution: 1★: 230 | 2★: 69 | 3★: 71 | 4★: 81 | 5★: 333
- Average review length: 52.5 words

## Combined

- Total reviews: **3782**
- Date range: 2017-08-25T20:34:31 to 2026-11-08T16:11:27
- Rating distribution: 1★: 1358 | 2★: 444 | 3★: 405 | 4★: 363 | 5★: 1212
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 503
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
