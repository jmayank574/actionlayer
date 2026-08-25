# WHOOP review dataset

Generated 2026-08-25T13:53:26.269377

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **4**
- Edited since last seen: 0
- Returned again, unchanged: 3332
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 108

## By source

### google_play

- Total reviews: **2882**
- Date range: 2017-08-25T20:34:31 to 2026-08-23T12:18:55
- Rating distribution: 1★: 1098 | 2★: 361 | 3★: 316 | 4★: 273 | 5★: 834
- Average review length: 37.8 words

### app_store

- Total reviews: **562**
- Date range: 2025-11-17T19:06:49 to 2026-08-23T20:39:55
- Rating distribution: 1★: 172 | 2★: 49 | 3★: 57 | 4★: 55 | 5★: 229
- Average review length: 55.4 words

## Combined

- Total reviews: **3444**
- Date range: 2017-08-25T20:34:31 to 2026-08-23T20:39:55
- Rating distribution: 1★: 1270 | 2★: 410 | 3★: 373 | 4★: 328 | 5★: 1063
- Average review length: 40.7 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 452
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
