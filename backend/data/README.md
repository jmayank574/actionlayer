# WHOOP review dataset

Generated 2026-11-13T20:23:21.632403

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **3**
- Edited since last seen: 0
- Returned again, unchanged: 3432
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 359

## By source

### google_play

- Total reviews: **3000**
- Date range: 2017-08-25T20:34:31 to 2026-11-11T06:29:40
- Rating distribution: 1★: 1129 | 2★: 375 | 3★: 334 | 4★: 283 | 5★: 879
- Average review length: 37.7 words

### app_store

- Total reviews: **794**
- Date range: 2025-11-17T19:06:49 to 2026-11-11T10:06:11
- Rating distribution: 1★: 232 | 2★: 70 | 3★: 72 | 4★: 81 | 5★: 339
- Average review length: 52.9 words

## Combined

- Total reviews: **3794**
- Date range: 2017-08-25T20:34:31 to 2026-11-11T10:06:11
- Rating distribution: 1★: 1361 | 2★: 445 | 3★: 406 | 4★: 364 | 5★: 1218
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 508
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
