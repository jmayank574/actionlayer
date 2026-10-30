# WHOOP review dataset

Generated 2026-10-30T18:28:45.370788

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **5**
- Edited since last seen: 0
- Returned again, unchanged: 3413
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 323

## By source

### google_play

- Total reviews: **2982**
- Date range: 2017-08-25T20:34:31 to 2026-10-29T14:20:41
- Rating distribution: 1★: 1126 | 2★: 374 | 3★: 332 | 4★: 281 | 5★: 869
- Average review length: 37.8 words

### app_store

- Total reviews: **759**
- Date range: 2025-11-17T19:06:49 to 2026-10-28T19:53:59
- Rating distribution: 1★: 221 | 2★: 65 | 3★: 69 | 4★: 77 | 5★: 327
- Average review length: 52.5 words

## Combined

- Total reviews: **3741**
- Date range: 2017-08-25T20:34:31 to 2026-10-29T14:20:41
- Rating distribution: 1★: 1347 | 2★: 439 | 3★: 401 | 4★: 358 | 5★: 1196
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 500
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
