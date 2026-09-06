# WHOOP review dataset

Generated 2026-09-06T16:02:28.369449

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **9**
- Edited since last seen: 0
- Returned again, unchanged: 3338
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 161

## By source

### google_play

- Total reviews: **2901**
- Date range: 2017-08-25T20:34:31 to 2026-09-04T20:03:32
- Rating distribution: 1★: 1100 | 2★: 365 | 3★: 320 | 4★: 276 | 5★: 840
- Average review length: 37.9 words

### app_store

- Total reviews: **607**
- Date range: 2025-11-17T19:06:49 to 2026-09-05T04:40:29
- Rating distribution: 1★: 185 | 2★: 52 | 3★: 59 | 4★: 60 | 5★: 251
- Average review length: 54.5 words

## Combined

- Total reviews: **3508**
- Date range: 2017-08-25T20:34:31 to 2026-09-05T04:40:29
- Rating distribution: 1★: 1285 | 2★: 417 | 3★: 379 | 4★: 336 | 5★: 1091
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 464
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
