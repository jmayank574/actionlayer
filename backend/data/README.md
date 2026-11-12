# WHOOP review dataset

Generated 2026-11-12T20:41:54.050379

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 0
- Returned again, unchanged: 3430
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 356

## By source

### google_play

- Total reviews: **3000**
- Date range: 2017-08-25T20:34:31 to 2026-11-11T06:29:40
- Rating distribution: 1★: 1129 | 2★: 375 | 3★: 334 | 4★: 283 | 5★: 879
- Average review length: 37.7 words

### app_store

- Total reviews: **791**
- Date range: 2025-11-17T19:06:49 to 2026-11-10T18:49:11
- Rating distribution: 1★: 231 | 2★: 70 | 3★: 72 | 4★: 81 | 5★: 337
- Average review length: 52.7 words

## Combined

- Total reviews: **3791**
- Date range: 2017-08-25T20:34:31 to 2026-11-11T06:29:40
- Rating distribution: 1★: 1360 | 2★: 445 | 3★: 406 | 4★: 364 | 5★: 1216
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 508
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
