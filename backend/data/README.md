# WHOOP review dataset

Generated 2026-08-30T17:15:45.840343

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **1**
- Edited since last seen: 0
- Returned again, unchanged: 3341
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 120

## By source

### google_play

- Total reviews: **2888**
- Date range: 2017-08-25T20:34:31 to 2026-08-29T13:54:22
- Rating distribution: 1★: 1098 | 2★: 363 | 3★: 317 | 4★: 275 | 5★: 835
- Average review length: 37.8 words

### app_store

- Total reviews: **574**
- Date range: 2025-11-17T19:06:49 to 2026-08-27T05:40:03
- Rating distribution: 1★: 176 | 2★: 49 | 3★: 58 | 4★: 56 | 5★: 235
- Average review length: 55.0 words

## Combined

- Total reviews: **3462**
- Date range: 2017-08-25T20:34:31 to 2026-08-29T13:54:22
- Rating distribution: 1★: 1274 | 2★: 412 | 3★: 375 | 4★: 331 | 5★: 1070
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 453
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
