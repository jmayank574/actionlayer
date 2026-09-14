# WHOOP review dataset

Generated 2026-09-14T18:26:33.163948

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 2
- Returned again, unchanged: 3356
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 193

## By source

### google_play

- Total reviews: **2917**
- Date range: 2017-08-25T20:34:31 to 2026-09-13T12:17:36
- Rating distribution: 1★: 1108 | 2★: 366 | 3★: 322 | 4★: 278 | 5★: 843
- Average review length: 37.8 words

### app_store

- Total reviews: **637**
- Date range: 2025-11-17T19:06:49 to 2026-09-12T08:19:12
- Rating distribution: 1★: 190 | 2★: 55 | 3★: 63 | 4★: 63 | 5★: 266
- Average review length: 53.8 words

## Combined

- Total reviews: **3554**
- Date range: 2017-08-25T20:34:31 to 2026-09-13T12:17:36
- Rating distribution: 1★: 1298 | 2★: 421 | 3★: 385 | 4★: 341 | 5★: 1109
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 470
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
