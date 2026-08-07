# Tagging pipeline notes — prompt stability investigation

Closed investigation. The tagging prompt (`tagging/prompt.py` + `tagging/few_shot.py`) is
back to its original, already-validated state — `data/tagged_reviews.csv` and
`data/eval_report.md` were never overwritten with any candidate version. This file
documents what was found so it isn't lost, and sets a standard for how future prompt
changes (including the ones logged in `data/taxonomy_v3_candidates.md`) should be tested.

## What was tested

Diagnosed two suspected weak spots from `data/eval_report.md`: `health_signal_reliability`
(3/3 eval mismatches) and `ai_coach` (looked bad on full-tag-set exact match, 3/13). Full
diagnosis found `ai_coach` wasn't actually broken — see the prior session's findings; no
prompt change was made there. `health_signal_reliability` had a real, confirmed bug: the
tagger fired on medical-adjacent keyword presence ("blood pressure", "EKG") rather than on
an actual reliability complaint or named diagnosis.

A fix was built (a dedicated instruction block + 2 more contrastive few-shot examples from
`data/open_coding.csv`) and tested three ways against the full 180-review `eval_sample.csv`:
combined, instructions-only, and few-shots-only.

## Finding: attention dilution, not a targeted bug

All three variants produced almost the same result: the same partial win on the target
category, and the same collateral regression on a consistent set of unrelated categories —
regardless of which piece of the fix was included. That rules out "the instruction text is
bad" or "the few-shot examples are bad" as the explanation. What's left is a property of the
prompt itself: at its current size (~45K characters), adding *anything* — content aimed at a
totally unrelated boundary — measurably hurts performance elsewhere. This is an attention/
dilution effect, not a defect in the specific content that was added.

## Victim categories (regressed in all three variants)

F1 on the 180-review eval set, baseline vs. each candidate:

| Subcategory | Support | Baseline F1 | Combined | Instructions-only | Few-shots-only |
|---|---|---|---|---|---|
| feature_ui_friction | 32 | 0.458 | 0.318 (−0.140) | 0.318 (−0.140) | 0.356 (−0.103) |
| build_quality_perception | 4 | 0.615 | 0.500 (−0.115) | 0.364 (−0.252) | 0.364 (−0.252) |
| support_responsiveness | 2 | 0.571 | 0.333 (−0.238) | 0.000 (−0.571) | 0.333 (−0.238) |
| sleep_alarm_ui | 1 | 0.667 | 0.400 (−0.267) | 0.400 (−0.267) | 0.500 (−0.167) |
| android_specific_bugs | 3 | 0.750 | 0.667 (−0.083) | 0.600 (−0.150) | 0.600 (−0.150) |
| update_failures | 10 | 0.667 | 0.556 (−0.111) | 0.588 (−0.078) | 0.588 (−0.078) |

`feature_ui_friction` is the one that matters most — it's the largest-support subcategory in
the eval set (32 of 180 reviews), so this isn't small-sample noise the way a 1-4-support
category's swing could be. Every variant lost real, previously-correct tags on it.

## What worked, for the record

- Borderline-pair swap count on `data_accuracy vs health_signal_reliability`: 2 → 1 in all
  three variants.
- False positives on `ecg_bp_feature_reliability`: 3 → 2 (confirmed for the combined
  variant) — the clean bug (firing on a purely positive ECG/blood-pressure mention) is fixed.
- None of this was enough to offset the collateral damage: subcategory micro-F1 went
  0.637 → 0.618–0.628 in every tested variant, all net negative.

## Practical implication for future prompt changes

This prompt cannot be assumed safe to extend just because a change targets a different,
unrelated category. **Every future addition — including any of the taxonomy v3 candidates in
`data/taxonomy_v3_candidates.md`, if one of them ever becomes a new subcategory that needs
prompt coverage — needs the same test before being adopted:**

1. Build the change as an isolated variant (don't bundle multiple changes together, or you
   can't tell which one caused what).
2. Re-tag only the 180 `eval_sample.csv` reviews with it (cheap — `revalidate_prompt_fix.py`
   already does this).
3. Compare **every** category's F1 before vs. after, not just the targeted one.
4. Only adopt if there's a net win — a fix that helps its target but regresses a
   higher-support category elsewhere is not automatically worth it.

Given this result, the prompt may also be approaching a size where it needs restructuring
(e.g., splitting into a shorter core + category-specific detail retrieved only when
relevant) rather than continuing to grow linearly — worth a design conversation before the
next addition, not just another isolated-variant test.

## One genuine taxonomy ambiguity found (not a tagger bug)

One of the three original `health_signal_reliability` mismatches (eval review
`babf2f38-3962-48c4-be89-be64899fccf1`: "ekg not functional blood pressure not accurate
sleep metrics accuracy is questionable") stayed a mismatch in every tested variant. On
inspection this isn't a tagger error — `ecg_bp_feature_reliability`'s current written
definition doesn't actually require a named diagnosis the way `cardiac_detection_trust`'s
does, so the tagger's read is defensible under the taxonomy as currently written. Logged as
candidate #4 in `data/taxonomy_v3_candidates.md` for the next taxonomy revision.

## Current state

`tagging/prompt.py` and `tagging/few_shot.py` are unmodified from the pre-investigation
baseline (verified: rebuilt system prompt is 45,320 characters, matching the original exactly).
`data/tagged_reviews.csv` was never opened for writing during this investigation.
`data/eval_report.md` was regenerated multiple times during scoring but always from the same
unchanged inputs (`data/tagged_reviews.csv` + `data/eval_sample.csv`), producing
byte-identical content each time. The full investigation output (candidate + variant A/B
predictions and reports) is archived in `data/_archive/`.
