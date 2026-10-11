# WHOOP review dataset

Generated 2026-10-11T17:56:26.184699

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **7**
- Edited since last seen: 0
- Returned again, unchanged: 3389
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 270

## By source

### google_play

- Total reviews: **2958**
- Date range: 2017-08-25T20:34:31 to 2026-10-10T12:46:07
- Rating distribution: 1★: 1117 | 2★: 371 | 3★: 330 | 4★: 281 | 5★: 859
- Average review length: 37.8 words

### app_store

- Total reviews: **708**
- Date range: 2025-11-17T19:06:49 to 2026-10-09T23:48:47
- Rating distribution: 1★: 208 | 2★: 64 | 3★: 65 | 4★: 70 | 5★: 301
- Average review length: 53.7 words

## Combined

- Total reviews: **3666**
- Date range: 2017-08-25T20:34:31 to 2026-10-10T12:46:07
- Rating distribution: 1★: 1325 | 2★: 435 | 3★: 395 | 4★: 351 | 5★: 1160
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 488
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
