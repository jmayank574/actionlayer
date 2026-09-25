# WHOOP review dataset

Generated 2026-09-25T17:49:43.329204

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **2**
- Edited since last seen: 1
- Returned again, unchanged: 3372
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 228

## By source

### google_play

- Total reviews: **2938**
- Date range: 2017-08-25T20:34:31 to 2026-09-24T04:26:28
- Rating distribution: 1★: 1112 | 2★: 370 | 3★: 325 | 4★: 281 | 5★: 850
- Average review length: 37.8 words

### app_store

- Total reviews: **665**
- Date range: 2025-11-17T19:06:49 to 2026-09-23T22:32:11
- Rating distribution: 1★: 196 | 2★: 60 | 3★: 62 | 4★: 66 | 5★: 281
- Average review length: 53.8 words

## Combined

- Total reviews: **3603**
- Date range: 2017-08-25T20:34:31 to 2026-09-24T04:26:28
- Rating distribution: 1★: 1308 | 2★: 430 | 3★: 387 | 4★: 347 | 5★: 1131
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 479
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
