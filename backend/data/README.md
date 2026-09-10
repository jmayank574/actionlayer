# WHOOP review dataset

Generated 2026-09-10T16:55:59.678324

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 1
- Returned again, unchanged: 3348
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 179

## By source

### google_play

- Total reviews: **2909**
- Date range: 2017-08-25T20:34:31 to 2026-09-09T12:59:38
- Rating distribution: 1★: 1104 | 2★: 365 | 3★: 322 | 4★: 277 | 5★: 841
- Average review length: 37.8 words

### app_store

- Total reviews: **624**
- Date range: 2025-11-17T19:06:49 to 2026-09-09T04:32:43
- Rating distribution: 1★: 188 | 2★: 54 | 3★: 63 | 4★: 62 | 5★: 257
- Average review length: 54.3 words

## Combined

- Total reviews: **3533**
- Date range: 2017-08-25T20:34:31 to 2026-09-09T12:59:38
- Rating distribution: 1★: 1292 | 2★: 419 | 3★: 385 | 4★: 339 | 5★: 1098
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 465
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
