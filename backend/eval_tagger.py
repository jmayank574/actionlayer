"""Eval harness (ActionLayer v2, step 3, Part 2). Scores the Part 1 tagger's
predictions (data/tagged_reviews.csv) against the hand-labeled held-out set
(data/eval_sample.csv) — the 180 reviews disjoint from the taxonomy-building
sample, never seen by the tagging prompt.

Never reads eval_sample.csv anywhere except here, for scoring.

Run with: python eval_tagger.py
"""

import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from tagging.taxonomy_loader import load_taxonomy, subcategory_to_parent_map, watch_category_ids

DATA_DIR = Path(__file__).parent / "data"
EVAL_PATH = DATA_DIR / "eval_sample.csv"
TAGGED_PATH = DATA_DIR / "tagged_reviews.csv"
REPORT_PATH = DATA_DIR / "eval_report.md"

BORDERLINE_PAIRS = [
    ("crashes_freezes", "data_sync_delays", "app_stability vs sync_connectivity"),
    ("metric_accuracy", ["cardiac_detection_trust", "ecg_bp_feature_reliability"], "data_accuracy vs health_signal_reliability"),
    ("sleep_alarm_ui", "redesign_regression", "sleep_tracking.sleep_alarm_ui vs ui_ux.redesign_regression"),
    ("device_rendering_bugs", "android_specific_bugs", "ui_ux.device_rendering_bugs vs platform_parity.android_specific_bugs"),
    ("ai_autonomy", "ai_only_support_channel", "ai_coach.ai_autonomy vs customer_support.ai_only_support_channel"),
]


def _parse_set(value) -> frozenset:
    if pd.isna(value) or str(value).strip() == "":
        return frozenset()
    return frozenset(x.strip() for x in str(value).split(";") if x.strip())


def load_data(tagged_path: Path = None):
    tagged_path = tagged_path or TAGGED_PATH
    taxonomy = load_taxonomy()
    parent_lookup = subcategory_to_parent_map(taxonomy)
    watch_ids = watch_category_ids(taxonomy)
    all_subcats = sorted(parent_lookup.keys())
    all_parents = sorted({c["id"] for c in taxonomy["categories"]})

    human = pd.read_csv(EVAL_PATH)
    human["review_id"] = human["review_id"].astype(str)
    human["h_subcats"] = human["subcategory_tags"].apply(_parse_set)
    human["h_parents"] = human["parent_category_tags"].apply(_parse_set)
    # eval_sample.csv's own "text" column has known encoding corruption from
    # whatever tool was used to hand-label it (46/180 rows, double-encoded
    # UTF-8 -- verified via raw byte inspection). It's dropped here and never
    # used for display; tagged_reviews.csv's "text" column (sourced straight
    # from whoop_reviews_raw.csv, verified clean) is the only text source
    # used in the report. Label columns are unaffected -- pure ASCII ids.
    human = human.drop(columns=["text"])

    pred = pd.read_csv(tagged_path)
    pred["review_id"] = pred["review_id"].astype(str)
    pred["p_subcats"] = pred["subcategory_tags"].apply(_parse_set)
    pred["p_parents"] = pred["parent_category_tags"].apply(_parse_set)
    pred["p_confidences"] = pred["confidences"].fillna("")

    eval_review_ids = set(human["review_id"])
    pred_eval = pred[pred["review_id"].isin(eval_review_ids)]

    merged = human.merge(
        pred_eval[["review_id", "p_subcats", "p_parents", "p_confidences", "text"]],
        on="review_id", how="left",
    )
    missing_pred = merged["p_subcats"].isna().sum()
    merged["p_subcats"] = merged["p_subcats"].apply(lambda x: x if isinstance(x, frozenset) else frozenset())
    merged["p_parents"] = merged["p_parents"].apply(lambda x: x if isinstance(x, frozenset) else frozenset())

    return merged, all_subcats, all_parents, parent_lookup, watch_ids, missing_pred


def per_category_prf(df: pd.DataFrame, categories: list[str], human_col: str, pred_col: str) -> pd.DataFrame:
    rows = []
    for cat in categories:
        tp = fp = fn = 0
        for _, r in df.iterrows():
            h = cat in r[human_col]
            p = cat in r[pred_col]
            if h and p:
                tp += 1
            elif p and not h:
                fp += 1
            elif h and not p:
                fn += 1
        precision = tp / (tp + fp) if (tp + fp) else float("nan")
        recall = tp / (tp + fn) if (tp + fn) else float("nan")
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) and not pd.isna(precision) and not pd.isna(recall) and (precision + recall) > 0 else (0.0 if (tp + fp + fn) > 0 else float("nan"))
        support = tp + fn
        rows.append({"category": cat, "support": support, "tp": tp, "fp": fp, "fn": fn,
                      "precision": precision, "recall": recall, "f1": f1})
    return pd.DataFrame(rows)


def micro_prf(prf_table: pd.DataFrame) -> dict:
    tp, fp, fn = prf_table["tp"].sum(), prf_table["fp"].sum(), prf_table["fn"].sum()
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else float("nan")
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def macro_f1(prf_table: pd.DataFrame, only_with_support: bool = False) -> float:
    t = prf_table[prf_table["support"] > 0] if only_with_support else prf_table
    return t["f1"].mean()


def jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def render_table(df: pd.DataFrame, cols: list[str], headers: list[str], fmt: dict) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in fmt:
                cells.append(fmt[c](v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def pct(v):
    return "n/a" if pd.isna(v) else f"{v:.1%}"


def num(v):
    return "n/a" if pd.isna(v) else f"{v:.3f}"


def main(tagged_path: Path = None, report_path: Path = None, source_label: str = None):
    tagged_path = tagged_path or TAGGED_PATH
    report_path = report_path or REPORT_PATH
    source_label = source_label or f"`{tagged_path.name}`"

    df, all_subcats, all_parents, parent_lookup, watch_ids, missing_pred = load_data(tagged_path)
    print(f"Loaded {len(df)} eval reviews. Missing predictions for {missing_pred} of them.")
    if missing_pred:
        print(f"WARNING: not all eval review_ids had a prediction in {tagged_path.name}.")

    # --- Subcategory-level metrics ---
    sub_prf = per_category_prf(df, all_subcats, "h_subcats", "p_subcats")
    sub_micro = micro_prf(sub_prf)
    sub_macro = macro_f1(sub_prf)
    sub_macro_supported = macro_f1(sub_prf, only_with_support=True)

    # --- Parent-level metrics ---
    par_prf = per_category_prf(df, all_parents, "h_parents", "p_parents")
    par_micro = micro_prf(par_prf)
    par_macro = macro_f1(par_prf)
    par_macro_supported = macro_f1(par_prf, only_with_support=True)

    # --- Multi-label exact match + Jaccard (subcategory level) ---
    df["exact_match"] = df.apply(lambda r: r["h_subcats"] == r["p_subcats"], axis=1)
    df["jaccard"] = df.apply(lambda r: jaccard(r["h_subcats"], r["p_subcats"]), axis=1)
    exact_match_rate = df["exact_match"].mean()
    mean_jaccard = df["jaccard"].mean()

    # Parent-level exact match too, for completeness
    df["exact_match_parent"] = df.apply(lambda r: r["h_parents"] == r["p_parents"], axis=1)
    exact_match_rate_parent = df["exact_match_parent"].mean()

    # --- Other/Ungrouped handling ---
    human_other = df[df["h_subcats"].apply(len) == 0]
    n_human_other = len(human_other)
    agree_other = (human_other["p_subcats"].apply(len) == 0).sum()
    forced_tag = n_human_other - agree_other

    # --- Borderline pair confusion ---
    pair_results = []
    for x, y, label in BORDERLINE_PAIRS:
        y_list = y if isinstance(y, list) else [y]

        def has_x(s, x=x):
            return x in s

        def has_y(s, y_list=y_list):
            return any(yy in s for yy in y_list)

        swap_x_to_y = 0  # human has X (not Y), pred has Y (not X)
        swap_y_to_x = 0  # human has Y (not X), pred has X (not Y)
        both_correct = 0
        both_missed = 0
        for _, r in df.iterrows():
            h_x, h_y = has_x(r["h_subcats"]), has_y(r["h_subcats"])
            p_x, p_y = has_x(r["p_subcats"]), has_y(r["p_subcats"])
            if h_x and not h_y and p_y and not p_x:
                swap_x_to_y += 1
            elif h_y and not h_x and p_x and not p_y:
                swap_y_to_x += 1
            elif (h_x or h_y) and ((h_x == p_x) and (h_y == p_y)):
                both_correct += 1
            elif (h_x or h_y) and not p_x and not p_y:
                both_missed += 1
        pair_results.append({
            "pair": label, "x": x, "y": ",".join(y_list),
            "swap_x_to_y": swap_x_to_y, "swap_y_to_x": swap_y_to_x,
            "total_swaps": swap_x_to_y + swap_y_to_x,
            "both_correct": both_correct, "both_missed": both_missed,
        })
    pair_df = pd.DataFrame(pair_results)

    # --- Watch categories qualitative pull ---
    watch_sections = {}
    for wid in sorted(watch_ids):
        touching = df[df["h_parents"].apply(lambda s, wid=wid: wid in s) | df["p_parents"].apply(lambda s, wid=wid: wid in s)]
        watch_sections[wid] = touching

    # --- Worst misses ---
    df["sym_diff_size"] = df.apply(lambda r: len(r["h_subcats"] ^ r["p_subcats"]), axis=1)
    worst = df[df["sym_diff_size"] > 0].sort_values(["sym_diff_size", "jaccard"], ascending=[False, True]).head(15)

    # ============ RENDER REPORT ============
    lines = []
    lines.append("# Tagger evaluation report — WHOOP (step 3, Part 2)\n")
    lines.append(f"Scored against `data/eval_sample.csv` — 180 reviews, disjoint from the "
                 f"180-review sample used to build the taxonomy, never seen by the tagging prompt "
                 f"as few-shot material. Predictions pulled from {source_label}.\n")
    if missing_pred:
        lines.append(f"**WARNING**: {missing_pred} eval review_ids had no prediction available.\n")

    lines.append("## Headline metrics\n")
    lines.append(f"- **Subcategory-level micro-F1**: {num(sub_micro['f1'])} "
                 f"(precision {num(sub_micro['precision'])}, recall {num(sub_micro['recall'])})")
    lines.append(f"- **Subcategory-level macro-F1**: {num(sub_macro)} (all 39 subcategories, "
                 f"zero-support ones counted) / {num(sub_macro_supported)} (only the "
                 f"{(sub_prf['support']>0).sum()} subcategories with at least 1 human-labeled example in this eval set)")
    lines.append(f"- **Parent-level micro-F1**: {num(par_micro['f1'])} "
                 f"(precision {num(par_micro['precision'])}, recall {num(par_micro['recall'])})")
    lines.append(f"- **Parent-level macro-F1**: {num(par_macro)} / {num(par_macro_supported)} "
                 f"(only the {(par_prf['support']>0).sum()} parents with support in this eval set)")
    lines.append(f"- **Multi-label exact-match rate** (subcategory set == human set exactly): {pct(exact_match_rate)}")
    lines.append(f"- **Multi-label exact-match rate** (parent set): {pct(exact_match_rate_parent)}")
    lines.append(f"- **Mean per-review Jaccard similarity** (subcategory level, partial credit): {num(mean_jaccard)}")
    lines.append(f"- **Other/Ungrouped agreement**: of {n_human_other} reviews the human left blank, "
                 f"the tagger also predicted zero tags on {agree_other} ({pct(agree_other/n_human_other if n_human_other else float('nan'))}) "
                 f"and forced at least one tag onto {forced_tag} ({pct(forced_tag/n_human_other if n_human_other else float('nan'))})")
    lines.append("")

    n_capped = df["notes"].fillna("").str.contains("capped at", case=False).sum() if "notes" in df.columns else 0
    lines.append("## Methodology note on the ground truth\n")
    lines.append(f"5 of 180 human labels ({n_capped} found via explicit \"capped at N\" language in "
                 f"`notes`) were deliberately capped at 3 tags even where the labeler's own notes say "
                 f"the review \"spans\" more issues — a conservative-labeling choice, not a taxonomy "
                 f"gap. This means some tagger \"false positives\" below are the tagger finding a real, "
                 f"additional, legitimate tag that the human chose not to record, not the tagger being "
                 f"wrong. This affects a small, identifiable slice of rows (visible in a few of the "
                 f"\"Worst individual misses\" below) — it is not the primary explanation for the "
                 f"broader precision gap, but it means precision numbers here are a slight "
                 f"underestimate of true tagger correctness.\n")

    lines.append("## Per-subcategory precision / recall / F1\n")
    lines.append("Sorted by support (human-labeled frequency in this eval set) descending. "
                 "`support` = number of eval reviews the human tagged with this subcategory.\n")
    sub_prf_sorted = sub_prf.sort_values("support", ascending=False)
    lines.append(render_table(
        sub_prf_sorted, ["category", "support", "tp", "fp", "fn", "precision", "recall", "f1"],
        ["Subcategory", "Support", "TP", "FP", "FN", "Precision", "Recall", "F1"],
        {"precision": pct, "recall": pct, "f1": num},
    ))
    lines.append("")

    lines.append("## Per-parent-category precision / recall / F1\n")
    par_prf_sorted = par_prf.sort_values("support", ascending=False)
    lines.append(render_table(
        par_prf_sorted, ["category", "support", "tp", "fp", "fn", "precision", "recall", "f1"],
        ["Parent category", "Support", "TP", "FP", "FN", "Precision", "Recall", "F1"],
        {"precision": pct, "recall": pct, "f1": num},
    ))
    lines.append("")

    lines.append("## Borderline-pair confusion analysis\n")
    lines.append("For each pair from `taxonomy_changelog.md`, a \"swap\" = the human tagged one side "
                 "of the pair (and not the other), and the tagger predicted the other side instead "
                 "(and not the first) — the exact failure mode the taxonomy fix was written to prevent. "
                 "`both_correct` = review touches the pair and the tagger got the X/Y presence exactly "
                 "right; `both_missed` = human tagged one of the pair, tagger predicted neither.\n")
    lines.append(render_table(
        pair_df, ["pair", "swap_x_to_y", "swap_y_to_x", "total_swaps", "both_correct", "both_missed"],
        ["Pair", "Swapped X→Y", "Swapped Y→X", "Total swaps", "Correctly resolved", "Missed entirely"],
        {},
    ))
    lines.append("")

    lines.append("## Watch categories — qualitative review\n")
    for wid in sorted(watch_ids):
        section = watch_sections[wid]
        lines.append(f"### {wid}\n")
        lines.append(f"{len(section)} eval review(s) touched by this category (human tag, predicted tag, or both).\n")
        if len(section) == 0:
            lines.append("No reviews in the eval set touched this category at all — zero signal to evaluate on.\n")
            continue
        for _, r in section.iterrows():
            h_str = ";".join(sorted(r["h_subcats"])) or "(none)"
            p_str = ";".join(sorted(r["p_subcats"])) or "(none)"
            match = "MATCH" if r["h_subcats"] == r["p_subcats"] else "MISMATCH"
            lines.append(f"- **[{match}]** review_id `{r['review_id']}` [{r['source']}, {r['rating']}-star]")
            lines.append(f"  - text: \"{r['text'][:300]}\"")
            lines.append(f"  - human: {h_str}")
            lines.append(f"  - predicted: {p_str}")
        lines.append("")

    lines.append("## Worst individual misses\n")
    lines.append("Ranked by size of the symmetric difference between human and predicted tag sets "
                 "(most disagreement first), tie-broken by lowest Jaccard.\n")
    for _, r in worst.iterrows():
        h_str = ";".join(sorted(r["h_subcats"])) or "(none — Other/Ungrouped)"
        p_str = ";".join(sorted(r["p_subcats"])) or "(none — Other/Ungrouped)"
        lines.append(f"### review_id `{r['review_id']}` [{r['source']}, {r['rating']}-star] — Jaccard {r['jaccard']:.2f}\n")
        lines.append(f"> {r['text']}\n")
        lines.append(f"- **Human**: {h_str}")
        if pd.notna(r.get("notes")):
            lines.append(f"  - human notes: {r['notes']}")
        lines.append(f"- **Predicted**: {p_str}")
        lines.append("")

    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Wrote {report_path}")
    print(f"\nHeadline: subcat micro-F1={sub_micro['f1']:.3f}, macro-F1={sub_macro_supported:.3f}, "
          f"exact-match={exact_match_rate:.1%}, mean Jaccard={mean_jaccard:.3f}, "
          f"Other agreement={agree_other}/{n_human_other}")

    return {
        "sub_prf": sub_prf, "par_prf": par_prf,
        "sub_micro": sub_micro, "par_micro": par_micro,
        "sub_macro": sub_macro, "sub_macro_supported": sub_macro_supported,
        "par_macro": par_macro, "par_macro_supported": par_macro_supported,
        "exact_match_rate": exact_match_rate, "exact_match_rate_parent": exact_match_rate_parent,
        "mean_jaccard": mean_jaccard,
        "n_human_other": n_human_other, "agree_other": agree_other, "forced_tag": forced_tag,
        "pair_df": pair_df,
    }


if __name__ == "__main__":
    main()
