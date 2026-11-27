# WHOOP review dataset

Generated 2026-11-27T21:51:23.946782

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 0
- Returned again, unchanged: 3458
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 394

## By source

### google_play

- Total reviews: **3027**
- Date range: 2017-08-25T20:34:31 to 2026-11-26T11:18:13
- Rating distribution: 1★: 1135 | 2★: 377 | 3★: 343 | 4★: 284 | 5★: 888
- Average review length: 37.7 words

### app_store

- Total reviews: **830**
- Date range: 2025-11-17T19:06:49 to 2026-11-25T03:44:32
- Rating distribution: 1★: 242 | 2★: 74 | 3★: 76 | 4★: 81 | 5★: 357
- Average review length: 52.7 words

## Combined

- Total reviews: **3857**
- Date range: 2017-08-25T20:34:31 to 2026-11-26T11:18:13
- Rating distribution: 1★: 1377 | 2★: 451 | 3★: 419 | 4★: 365 | 5★: 1245
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 510
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
