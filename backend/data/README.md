# WHOOP review dataset

Generated 2026-08-16T13:34:16.862030

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **13**
- Edited since last seen: 0
- Returned again, unchanged: 3307
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 72

## By source

### google_play

- Total reviews: **2867**
- Date range: 2017-08-25T20:34:31 to 2026-08-15T11:04:19
- Rating distribution: 1★: 1094 | 2★: 360 | 3★: 314 | 4★: 272 | 5★: 827
- Average review length: 37.8 words

### app_store

- Total reviews: **525**
- Date range: 2025-11-17T19:06:49 to 2026-08-15T03:18:31
- Rating distribution: 1★: 163 | 2★: 46 | 3★: 55 | 4★: 54 | 5★: 207
- Average review length: 56.1 words

## Combined

- Total reviews: **3392**
- Date range: 2017-08-25T20:34:31 to 2026-08-15T11:04:19
- Rating distribution: 1★: 1257 | 2★: 406 | 3★: 369 | 4★: 326 | 5★: 1034
- Average review length: 40.6 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 447
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
