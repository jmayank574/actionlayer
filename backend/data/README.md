# WHOOP review dataset

Generated 2026-08-15T13:33:24.370109

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **6**
- Edited since last seen: 0
- Returned again, unchanged: 3309
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 64

## By source

### google_play

- Total reviews: **2862**
- Date range: 2017-08-25T20:34:31 to 2026-08-13T15:09:14
- Rating distribution: 1★: 1094 | 2★: 359 | 3★: 313 | 4★: 272 | 5★: 824
- Average review length: 37.8 words

### app_store

- Total reviews: **517**
- Date range: 2025-11-17T19:06:49 to 2026-08-13T12:09:52
- Rating distribution: 1★: 163 | 2★: 45 | 3★: 52 | 4★: 53 | 5★: 204
- Average review length: 54.7 words

## Combined

- Total reviews: **3379**
- Date range: 2017-08-25T20:34:31 to 2026-08-13T15:09:14
- Rating distribution: 1★: 1257 | 2★: 404 | 3★: 365 | 4★: 325 | 5★: 1028
- Average review length: 40.4 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 448
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
