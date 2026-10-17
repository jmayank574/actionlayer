# WHOOP review dataset

Generated 2026-10-17T16:11:51.819912

Every row below came from a live Google Play or Apple App Store response — nothing in this dataset is model-generated, inferred, or backfilled. Counts reflect exactly what each source returned.

## Since last pull

- New reviews: **10**
- Edited since last seen: 2
- Returned again, unchanged: 3392
- Carried over from a prior pull (not returned this time, e.g. aged out of Apple's ~500-review RSS window): 292

## By source

### google_play

- Total reviews: **2967**
- Date range: 2017-08-25T20:34:31 to 2026-10-16T01:45:05
- Rating distribution: 1★: 1121 | 2★: 373 | 3★: 330 | 4★: 281 | 5★: 862
- Average review length: 37.8 words

### app_store

- Total reviews: **729**
- Date range: 2025-11-17T19:06:49 to 2026-10-16T06:27:01
- Rating distribution: 1★: 213 | 2★: 65 | 3★: 67 | 4★: 72 | 5★: 312
- Average review length: 53.3 words

## Combined

- Total reviews: **3696**
- Date range: 2017-08-25T20:34:31 to 2026-10-16T06:27:01
- Rating distribution: 1★: 1334 | 2★: 438 | 3★: 397 | 4★: 353 | 5★: 1174
- Average review length: 40.8 words

## Filtering applied

- Dropped as empty/near-empty (<5 words): 490
- Dropped as duplicates (same review_id + text): 0
- No filtering by rating, sentiment, or topic — this is the full unfiltered distribution, 5-star reviews included.

## Rate-limiting / access issues hit during this pull

- App Store: hit Apple's 10-page RSS cap (~500 reviews) — this is a limit of Apple's public feed, not a failure of the pull. Apple does not expose full review history through any public endpoint.
