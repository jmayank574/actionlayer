# WHOOP review dataset

Generated 2026-10-03T17:05:10.198134

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **2**
- Edited since last seen: 0
- Returned again, unchanged: 3389
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 240

## By source

### google_play

- Total reviews: **2951**
- Date range: 2017-08-25T20:34:31 to 2026-10-02T13:13:58
- Rating distribution: 1★: 1115 | 2★: 370 | 3★: 329 | 4★: 280 | 5★: 857
- Average review length: 37.8 words

### app_store

- Total reviews: **680**
- Date range: 2025-11-17T19:06:49 to 2026-10-01T04:24:13
- Rating distribution: 1★: 201 | 2★: 60 | 3★: 64 | 4★: 68 | 5★: 287
- Average review length: 53.9 words

## Combined

- Total reviews: **3631**
- Date range: 2017-08-25T20:34:31 to 2026-10-02T13:13:58
- Rating distribution: 1★: 1316 | 2★: 430 | 3★: 393 | 4★: 348 | 5★: 1144
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 483
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
