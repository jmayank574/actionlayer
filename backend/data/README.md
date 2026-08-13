# WHOOP review dataset

Generated 2026-08-13T14:23:17.029156

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **8**
- Edited since last seen: 0
- Returned again, unchanged: 3303
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 56

## By source

### google_play

- Total reviews: **2857**
- Date range: 2017-08-25T20:34:31 to 2026-08-12T12:49:06
- Rating distribution: 1★: 1094 | 2★: 358 | 3★: 312 | 4★: 272 | 5★: 821
- Average review length: 37.8 words

### app_store

- Total reviews: **510**
- Date range: 2025-11-17T19:06:49 to 2026-08-11T12:48:45
- Rating distribution: 1★: 159 | 2★: 44 | 3★: 52 | 4★: 53 | 5★: 202
- Average review length: 54.6 words

## Combined

- Total reviews: **3367**
- Date range: 2017-08-25T20:34:31 to 2026-08-12T12:49:06
- Rating distribution: 1★: 1253 | 2★: 402 | 3★: 364 | 4★: 325 | 5★: 1023
- Average review length: 40.4 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 445
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
