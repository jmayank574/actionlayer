"""Regression gate for the tagger, built on the existing hand-labeled held-out
set (data/eval_sample.csv, 180 reviews) and scoring code (eval_tagger.py).

Before this, tagger accuracy had been measured once, by hand (data/eval_report.md).
Nothing re-ran it when the prompt, taxonomy, or model changed -- so a change
that quietly made tagging worse would ship silently. This makes the last good
result a committed baseline (evals/baseline_tagger.json) and fails when a
change drops below it.

Modes (from backend/):
  python -m evals.tagger_eval                    FREE, informational. Prints the scores of the
                                                 predictions already stored in
                                                 data/tagged_reviews.csv. Never gates: those were
                                                 made by an earlier run, so comparing them to a
                                                 fresh re-tag is not like-for-like.
  python -m evals.tagger_eval --retag            PAID (~180 reviews of model calls). Re-tags the
                                                 eval reviews with the CURRENT prompt/taxonomy and
                                                 gates against the baseline. This is the real
                                                 regression test -- run it whenever tagging/,
                                                 taxonomy.yaml, or the model changes.
  python -m evals.tagger_eval --retag --update-baseline
                                                 After a deliberate, reviewed change: record the
                                                 new scores as the baseline. (Baseline can only
                                                 come from a re-tag, the same procedure it is
                                                 checked with.)

Why re-tag-vs-re-tag: the first version compared a fresh re-tag to stored
predictions, and with the tagger at the API's default randomness an UNCHANGED
prompt scored ~0.04 lower (26% of reviews changed tags between identical runs).
The tagger now runs at temperature 0, so repeat runs match closely; the
tolerance below only has to absorb small residual variation.

Gating: aggregate metrics may drop by at most TOLERANCE (absolute). Per-subcategory
drops are reported as warnings only -- with ~5 examples per category they are too
noisy to gate on.
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent))
import eval_tagger  # noqa: E402  (existing scoring code; reused, not duplicated)

BASELINE_PATH = Path(__file__).parent / "baseline_tagger.json"
CANDIDATE_PATH = Path(__file__).parent / "results" / "tagger_candidate.csv"

TOLERANCE = 0.03            # max allowed absolute drop in a gated aggregate metric
CATEGORY_WARN_DROP = 0.15   # per-subcategory F1 drop worth flagging (not gating)
CATEGORY_MIN_SUPPORT = 6    # ignore categories with too few eval examples to mean anything

GATED = {
    "sub_micro_f1": "Subcategory micro-F1",
    "par_micro_f1": "Parent micro-F1",
    "mean_jaccard": "Mean Jaccard (partial credit)",
}

# "Other/Ungrouped agreement" is measured on only the ~24 eval reviews the human
# left untagged, so ONE review changing moves it by 0.042 -- more than the gate
# tolerance -- and it tripped the gate on a healthy repeat run. Reported, and
# warned on only when it falls by ~3 reviews' worth, never gated.
OTHER_WARN_DROP = 0.09


def _clean(x):
    return None if isinstance(x, float) and math.isnan(x) else x


def compute_metrics(tagged_path: Path) -> dict:
    df, all_subcats, all_parents, _parent_lookup, _watch, missing = eval_tagger.load_data(tagged_path)
    sub_prf = eval_tagger.per_category_prf(df, all_subcats, "h_subcats", "p_subcats")
    par_prf = eval_tagger.per_category_prf(df, all_parents, "h_parents", "p_parents")

    human_other = df[df["h_subcats"].apply(len) == 0]
    other_agree = (human_other["p_subcats"].apply(len) == 0).sum() / len(human_other) if len(human_other) else float("nan")
    jacc = df.apply(lambda r: eval_tagger.jaccard(r["h_subcats"], r["p_subcats"]), axis=1).mean()

    return {
        "n_eval_reviews": int(len(df)),
        "missing_predictions": int(missing),
        "sub_micro_f1": _clean(round(eval_tagger.micro_prf(sub_prf)["f1"], 4)),
        "par_micro_f1": _clean(round(eval_tagger.micro_prf(par_prf)["f1"], 4)),
        "sub_macro_f1_supported": _clean(round(eval_tagger.macro_f1(sub_prf, only_with_support=True), 4)),
        "other_agreement": _clean(round(float(other_agree), 4)),
        "mean_jaccard": _clean(round(float(jacc), 4)),
        "per_subcategory": {
            r["category"]: {"support": int(r["support"]), "f1": _clean(round(r["f1"], 4))}
            for _, r in sub_prf.iterrows() if r["support"] > 0
        },
    }


def compare(baseline: dict, current: dict) -> tuple[list[str], list[str]]:
    failures, warnings = [], []
    if current["missing_predictions"]:
        failures.append(f"{current['missing_predictions']} eval review(s) have no prediction")
    print(f"{'metric':32s} {'baseline':>9s} {'current':>9s} {'delta':>8s}")
    for key, label in GATED.items():
        b, c = baseline[key], current[key]
        if b is None or c is None:
            failures.append(f"{label} could not be computed (baseline={b}, current={c})")
            continue
        delta = c - b
        flag = ""
        if delta < -TOLERANCE:
            failures.append(f"{label} dropped {b:.3f} -> {c:.3f} (more than {TOLERANCE})")
            flag = "  <-- REGRESSION"
        print(f"{label:32s} {b:9.3f} {c:9.3f} {delta:+8.3f}{flag}")

    b_o, c_o = baseline["other_agreement"], current["other_agreement"]
    if b_o is not None and c_o is not None:
        print(f"{'Other/Ungrouped agreement (info)':32s} {b_o:9.3f} {c_o:9.3f} {c_o - b_o:+8.3f}")
        if c_o < b_o - OTHER_WARN_DROP:
            warnings.append(f"Other/Ungrouped agreement fell {b_o:.2f} -> {c_o:.2f} (n=~24, so each review is ~0.04)")

    for cat, b in baseline["per_subcategory"].items():
        c = current["per_subcategory"].get(cat)
        if b["support"] < CATEGORY_MIN_SUPPORT or b["f1"] is None:
            continue
        cf1 = c["f1"] if c and c["f1"] is not None else 0.0
        if cf1 < b["f1"] - CATEGORY_WARN_DROP:
            warnings.append(f"{cat} F1 {b['f1']:.2f} -> {cf1:.2f} (support {b['support']})")
    return failures, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retag", action="store_true", help="re-tag the eval reviews with the current prompt (costs API money)")
    parser.add_argument("--update-baseline", action="store_true", help="write the scored result as the new baseline")
    args = parser.parse_args()

    if args.update_baseline and not args.retag:
        print("ERROR: --update-baseline requires --retag (the baseline must come from the same "
              "procedure it is checked with, not from stored predictions).", file=sys.stderr)
        return 2

    if args.retag:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
        from evals.preflight import api_error
        problem = api_error()
        if problem:
            print(f"ERROR: --retag makes real model calls, but the API isn't usable: {problem}", file=sys.stderr)
            return 2
        import revalidate_prompt_fix  # noqa: E402
        CANDIDATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        n_ok = revalidate_prompt_fix.retag_eval_reviews(CANDIDATE_PATH)
        print(f"{n_ok} eval reviews re-tagged with the current prompt.\n")
        if n_ok == 0:
            # An empty result can't be scored, and isn't a regression -- it's a broken run.
            print("ERROR: none of the eval reviews could be re-tagged; nothing to score.", file=sys.stderr)
            return 2
        scored_path, source = CANDIDATE_PATH, "re-tagged with the current prompt"
    else:
        scored_path, source = eval_tagger.TAGGED_PATH, "stored predictions in data/tagged_reviews.csv"

    current = compute_metrics(scored_path)
    print(f"Scored {current['n_eval_reviews']} hand-labeled reviews ({source}).\n")

    if not args.retag:
        for key, label in GATED.items():
            print(f"  {label}: {current[key]:.3f}")
        print("\nInformational only -- these are stored predictions from an earlier run, so nothing "
              "is gated. Use --retag to test the current prompt.")
        return 0

    if args.update_baseline:
        BASELINE_PATH.write_text(json.dumps(current, indent=2), encoding="utf-8")
        print(f"Baseline written to {BASELINE_PATH}")
        for key, label in GATED.items():
            print(f"  {label}: {current[key]:.3f}")
        return 0

    if not BASELINE_PATH.exists():
        print("No baseline yet -- run with --update-baseline first.", file=sys.stderr)
        return 2
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    failures, warnings = compare(baseline, current)

    for w in warnings:
        print(f"  ! {w}")
    if failures:
        print("\nFAILED:")
        for f in failures:
            print(f"  x {f}")
        return 1
    print("\nPASSED: no gated metric dropped more than the tolerance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
