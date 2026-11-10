# WHOOP review dataset

Generated 2026-11-10T20:20:44.889516

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **4**
- Edited since last seen: 0
- Returned again, unchanged: 3431
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 351

## By source

### google_play

- Total reviews: **2999**
- Date range: 2017-08-25T20:34:31 to 2026-11-09T02:19:17
- Rating distribution: 1★: 1128 | 2★: 375 | 3★: 334 | 4★: 283 | 5★: 879
- Average review length: 37.7 words

### app_store

- Total reviews: **787**
- Date range: 2025-11-17T19:06:49 to 2026-11-09T07:38:49
- Rating distribution: 1★: 230 | 2★: 69 | 3★: 71 | 4★: 81 | 5★: 336
- Average review length: 52.5 words

## Combined

- Total reviews: **3786**
- Date range: 2017-08-25T20:34:31 to 2026-11-09T07:38:49
- Rating distribution: 1★: 1358 | 2★: 444 | 3★: 405 | 4★: 364 | 5★: 1215
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 503
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
