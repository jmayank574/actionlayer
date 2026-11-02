# WHOOP review dataset

Generated 2026-11-02T22:13:30.246969

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **7**
- Edited since last seen: 0
- Returned again, unchanged: 3415
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 333

## By source

### google_play

- Total reviews: **2987**
- Date range: 2017-08-25T20:34:31 to 2026-10-31T20:22:25
- Rating distribution: 1★: 1127 | 2★: 374 | 3★: 332 | 4★: 281 | 5★: 873
- Average review length: 37.7 words

### app_store

- Total reviews: **768**
- Date range: 2025-11-17T19:06:49 to 2026-10-31T06:34:08
- Rating distribution: 1★: 224 | 2★: 66 | 3★: 69 | 4★: 80 | 5★: 329
- Average review length: 52.7 words

## Combined

- Total reviews: **3755**
- Date range: 2017-08-25T20:34:31 to 2026-10-31T20:22:25
- Rating distribution: 1★: 1351 | 2★: 440 | 3★: 401 | 4★: 361 | 5★: 1202
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 500
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
