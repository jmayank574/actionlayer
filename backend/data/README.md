# WHOOP review dataset

Generated 2026-10-13T19:47:33.801038

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **1**
- Edited since last seen: 0
- Returned again, unchanged: 3394
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 276

## By source

### google_play

- Total reviews: **2958**
- Date range: 2017-08-25T20:34:31 to 2026-10-10T12:46:07
- Rating distribution: 1★: 1117 | 2★: 371 | 3★: 330 | 4★: 281 | 5★: 859
- Average review length: 37.8 words

### app_store

- Total reviews: **713**
- Date range: 2025-11-17T19:06:49 to 2026-10-11T07:03:47
- Rating distribution: 1★: 209 | 2★: 64 | 3★: 66 | 4★: 70 | 5★: 304
- Average review length: 53.5 words

## Combined

- Total reviews: **3671**
- Date range: 2017-08-25T20:34:31 to 2026-10-11T07:03:47
- Rating distribution: 1★: 1326 | 2★: 435 | 3★: 396 | 4★: 351 | 5★: 1163
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 489
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
