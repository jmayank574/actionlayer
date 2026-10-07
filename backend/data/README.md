# WHOOP review dataset

Generated 2026-10-07T19:15:20.428817

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 0
- Returned again, unchanged: 3386
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 255

## By source

### google_play

- Total reviews: **2952**
- Date range: 2017-08-25T20:34:31 to 2026-10-06T05:18:44
- Rating distribution: 1★: 1115 | 2★: 370 | 3★: 329 | 4★: 281 | 5★: 857
- Average review length: 37.8 words

### app_store

- Total reviews: **694**
- Date range: 2025-11-17T19:06:49 to 2026-10-05T20:09:22
- Rating distribution: 1★: 204 | 2★: 61 | 3★: 64 | 4★: 69 | 5★: 296
- Average review length: 54.0 words

## Combined

- Total reviews: **3646**
- Date range: 2017-08-25T20:34:31 to 2026-10-06T05:18:44
- Rating distribution: 1★: 1319 | 2★: 431 | 3★: 393 | 4★: 350 | 5★: 1153
- Average review length: 40.9 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 484
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
