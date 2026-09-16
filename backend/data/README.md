# WHOOP review dataset

Generated 2026-09-16T17:33:15.916647

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 0
- Returned again, unchanged: 3357
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 198

## By source

### google_play

- Total reviews: **2918**
- Date range: 2017-08-25T20:34:31 to 2026-09-14T16:08:25
- Rating distribution: 1★: 1109 | 2★: 366 | 3★: 322 | 4★: 278 | 5★: 843
- Average review length: 37.8 words

### app_store

- Total reviews: **642**
- Date range: 2025-11-17T19:06:49 to 2026-09-14T19:34:31
- Rating distribution: 1★: 192 | 2★: 57 | 3★: 62 | 4★: 62 | 5★: 269
- Average review length: 53.7 words

## Combined

- Total reviews: **3560**
- Date range: 2017-08-25T20:34:31 to 2026-09-14T19:34:31
- Rating distribution: 1★: 1301 | 2★: 423 | 3★: 384 | 4★: 340 | 5★: 1112
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 470
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
