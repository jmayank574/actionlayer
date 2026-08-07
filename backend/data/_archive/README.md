# Archive

Superseded/intermediate files, kept for audit trail rather than deleted. Nothing here is
current or referenced by any script — the working files live in `data/` proper.

## health_signal_reliability prompt investigation (2026-08-05)

`eval_report_candidate.md`, `eval_report_variantA_instr_only.md`,
`eval_report_variantB_fewshot_only.md`, `tagged_reviews_eval_candidate.csv`,
`tagged_reviews_eval_variantA_instr_only.csv`, `tagged_reviews_eval_variantB_fewshot_only.csv`
— the three tested prompt variants (combined fix, instructions-only, few-shots-only) from the
`health_signal_reliability` prompt-tightening investigation. None were adopted (all three
regressed the eval score overall). See `data/tagging_pipeline_notes.md` for the actual
finding — the prompt shows attention-dilution regression on any addition at its current size,
not a defect specific to what was tried. `data/tagged_reviews.csv` and `data/eval_report.md`
remain the current validated baseline and were never replaced by any of these.
