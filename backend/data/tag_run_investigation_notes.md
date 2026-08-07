# Full-dataset tagging run — investigation notes (Part 1)

Run: `tag_reviews.py`, full 3,295-review dataset, 2026-08-05. 100% coverage
(3,295/3,295), 0 hard failures, 77/5,333 (1.44%) tag attempts dropped for
using an invalid subcategory id (not logged individually — see Limitations
below). Output: `data/tagged_reviews.csv`, raw stats: `data/tag_run_stats.json`.

Both reference-range checks flagged on this run. Investigated both before
accepting or rejecting the result — findings below.

## Other/Ungrouped: 19.2% vs. 10-15% reference — mostly a composition artifact

- Spot-checked 20 random Other-tagged reviews: same pattern as the 180-sample's
  Other bucket (undifferentiated praise — "Great app!", "5 stars", "Fantastic
  app!!!"). No sign of genuine complaints being wrongly dumped into Other.
- Other-rate is sharply rating-dependent: 58.2% of 5-star reviews landed in
  Other vs. ~1-2% of 1-3 star and 7.5% of 4-star.
- The 180-review reference sample was deliberately rebalanced to 20% per
  rating (1-5), per the original sampling brief ("don't over-index on
  1-star"). The full dataset's natural rating mix is 37.5% / 12.1% / 10.8% /
  9.7% / 29.9% (1-5 star) — meaningfully more 5-star-heavy than the sample.
- Reweighting the full run's own per-rating Other-rates to the sample's 20%-
  each mix: **14.1%**, landing at the edge of the 10-15% reference range (vs.
  10.6% actual). Most of the gap is explained by this composition mismatch;
  the remaining ~3.5pp could be sampling noise in a 180-review reference.
- **Conclusion: not a red flag on the tagger.** The reference range itself
  wasn't population-representative — it was built from a sample intentionally
  skewed away from the rating band that produces most Other-tagged reviews.

## Multi-label: 49.6% vs. 35-40% reference — real gap, cause unresolved

- The same reweighting trick makes this *worse* (51.8% reweighted), so
  composition doesn't explain it.
- Spot-checked 12 reviews with 4-5 tags: all legitimate multi-issue reviews
  (e.g., a review naming a device failure, AI-only support, a billing
  dispute, and price in one paragraph — four real, distinct complaints, not
  one complaint tagged four ways).
- Working hypothesis, not confirmed: the original 180-review open-coding pass
  (which set the 37.8% reference) may itself have been less exhaustive than
  this tagger — a human skimming for the main issues in a review vs. a
  process explicitly instructed to check every subcategory's boundary text
  against every review. Equally plausible: the tagger is over-triggering on
  loosely-related language. **Cannot distinguish these without ground truth.**
- **This should be the first thing checked once `data/eval_sample.csv` is
  hand-labeled and Part 2 runs** — Jaccard/precision/recall against real
  human labels will show directly whether the extra tags are correct
  (undercounted reference) or wrong (over-tagging tagger).

## Secondary observation: parent-category distribution shift

Full-run parent-category tag counts (3,295 reviews) vs. 180-sample counts
(from `taxonomy_notes.md`):

| Parent | 180-sample count | Full-run count | Full-run % of reviews |
|---|---|---|---|
| pricing_billing | 41 | 1,053 | 32.0% |
| sync_connectivity | 27 | 811 | 24.6% |
| app_stability | 16 | 508 | 15.4% |
| customer_support | 24 | 504 | 15.3% |
| sleep_tracking | 15 | 426 | 12.9% |
| ui_ux | 24 | 405 | 12.3% |
| feature_requests | 29 | 391 | 11.9% |
| data_accuracy | 27 | 359 | 10.9% |
| platform_parity | 9 | 326 | 9.9% |
| hardware_wearability | 22 | 267 | 8.1% |
| ai_coach | 10 | 135 | 4.1% |
| localization | 9 | 39 | 1.2% |
| health_signal_reliability | 2 | 32 | 1.0% |

Top and bottom of the ranking hold (pricing_billing #1, health_signal_reliability
and localization at the bottom in both). The notable mover: `sync_connectivity`
went from mid-pack in the 180-sample to the **2nd-largest category at full
scale**. Same open question as multi-label — real signal the small sample
under-captured, or the tagger over-triggering on sync-adjacent language (the
category with the most subtle boundary text — see `data_sync_delays`'s
"laggy" clarification in `taxonomy_changelog.md`). Worth specific attention
in the Part 2 confusion analysis once eval labels exist.

## Confidence distribution

5,256 valid tags assigned (77 more attempted but dropped as invalid ids).
59.8% high, 36.4% medium, 3.8% low. Not yet validated against ground truth —
whether "high confidence" actually correlates with "correct" is a Part 2
question.

## Limitations of this run, for the record

- Individual invalid subcategory ids (the 77 dropped) were not logged one by
  one — only the count. If a systematic pattern exists (e.g. the model
  consistently inventing a plausible-but-wrong id), it isn't visible from
  this run's output. Worth adding per-id logging before the next full run.
- This investigation is diagnostic, not a substitute for Part 2. Every
  conclusion above about "is this correct" is provisional until scored
  against `data/eval_sample.csv`.
