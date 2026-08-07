# Eval sample — WHOOP, step 2.5

A held-out sample for evaluating the step-3 tagger, disjoint from
`data/taxonomy_sample.csv` (the 180 reviews the taxonomy's category boundaries
were written to fit). Reusing that sample to evaluate the tagger would measure
agreement with its own training examples, not generalization — this file
exists so the eval is honest.

**This file is unlabeled by design.** `parent_category_tags`,
`subcategory_tags`, and `notes` are empty in `data/eval_sample.csv` and were
not pre-filled, drafted, or suggested by any automated process. Labeling it is
a manual step for you to do before step 3.

## Sample size and stratification

180 reviews, stratified by source × rating × time period — same method as the
original `taxonomy_sample.csv` (`sample_for_taxonomy.py`), reused unchanged in
`sample_eval_set.py` so the two samples are comparable in composition.

| source | 1★ | 2★ | 3★ | 4★ | 5★ |
|---|---|---|---|---|---|
| google_play | 23 | 24 | 22 | 22 | 24 |
| app_store | 14 | 12 | 12 | 14 | 13 |

## Overlap check (shown, not just asserted)

Run against the full 3,295-review raw dataset:

1. **review_id check**: all 180 of the original sample's `review_id`s were
   confirmed present in the raw dataset (180/180), then excluded from the
   candidate pool: 3,295 → 3,115 rows.
2. **Exact text check (backup)**: of the 3,115 rows remaining after the
   review_id exclusion, 0 still matched an original review's exact `text`.
   review_id turned out to be a sufficient key on its own here, but the text
   check ran anyway rather than assuming that.
3. **Post-sampling re-check**: after drawing the final 180-row eval sample
   from the disjoint pool, re-checked the sample itself (not just the pool it
   was drawn from) against both the original review_ids and texts — 0 matches
   on either.

Result: **0 of 180 eval reviews overlap with the original 180-review sample**,
verified by id, by text, and again post-sampling.

## Reproducibility

- Script: `sample_eval_set.py` (run with `python sample_eval_set.py`)
- Seed: **101** (the original taxonomy-building sample used seed 42 in
  `sample_for_taxonomy.py` — deliberately different so the two draws are
  auditably independent, not just coincidentally non-overlapping)
- Source: `data/whoop_reviews_raw.csv`, with `data/taxonomy_sample.csv`
  excluded before sampling

## How to fill in the label columns

Same rules as the original open-coding pass (`data/taxonomy_notes.md`) —
consistency with that method is what makes this a fair comparison:

- **`parent_category_tags`**: the `id` field(s) from `data/taxonomy.yaml`'s
  top-level `categories` (e.g. `pricing_billing`, `sleep_tracking`). Use the
  exact ids as written in the yaml, not the display names.
- **`subcategory_tags`**: the matching subcategory `id`(s) (e.g.
  `price_value_perception`, `sleep_accuracy`). If you tag a subcategory, tag
  its parent too, in the same order, so the two columns line up pair-by-pair.
- **Multi-label is expected, not exceptional** — the original pass found
  37.8% of reviews carried 2+ tags. Separate multiple tags with `;` (matching
  `data/open_coding.csv`'s convention), e.g.
  `parent_category_tags: pricing_billing;hardware_wearability` /
  `subcategory_tags: price_value_perception;strap_clasp_durability`.
- **Leave both columns blank if nothing in the taxonomy fits** — don't
  force-fit into the nearest category. The original pass landed 10.6% of
  reviews in Other/Ungrouped; a similar or different rate here is real signal
  about the taxonomy, not something to correct for by fitting harder.
- **`notes`** is free text — use it for anything ambiguous: a review that
  felt borderline between two subcategories, one where you had to guess at
  the taxonomy's intent, or one that suggests a gap the taxonomy doesn't
  cover. These notes are exactly the kind of thing that should inform any
  taxonomy revision after step 3, not just the tagger's accuracy score.

## Files

- `data/eval_sample.csv` — the 180 unlabeled reviews (schema: `eval_id`,
  `source`, `review_id`, `rating`, `date`, `text`, `app_version`, `country`,
  `parent_category_tags`, `subcategory_tags`, `notes`)
- `sample_eval_set.py` — the script that produced it, reproducible
