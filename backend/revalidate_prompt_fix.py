"""Cheap re-validation of the health_signal_reliability prompt fix (ActionLayer
v2, step 3, diagnostic session): re-tags ONLY the 180 eval_sample.csv reviews
with the updated prompt, scores against eval_sample.csv, and prints a full
per-category before/after comparison.

Does NOT touch data/tagged_reviews.csv (the full 3,295-review file) or
data/eval_report.md (the baseline report) — writes to
data/tagged_reviews_eval_candidate.csv and data/eval_report_candidate.md
instead, so the baseline stays intact for comparison and nothing is
overwritten without an explicit decision to proceed.

eval_sample.csv is read only to get the list of review_ids to re-tag and for
scoring — never as prompt/few-shot material (few-shot still comes from
tagging/few_shot.py, which only reads open_coding.csv).

Run with: python revalidate_prompt_fix.py
"""

import csv
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from tagging.prompt import build_system_prompt
from tagging.tagger import tag_all
from tagging.taxonomy_loader import load_taxonomy, valid_subcategory_ids

import eval_tagger

DATA_DIR = Path(__file__).parent / "data"
RAW_PATH = DATA_DIR / "whoop_reviews_raw.csv"
EVAL_PATH = DATA_DIR / "eval_sample.csv"
CANDIDATE_TAGGED_PATH = DATA_DIR / "tagged_reviews_eval_candidate.csv"
CANDIDATE_REPORT_PATH = DATA_DIR / "eval_report_candidate.md"


def retag_eval_reviews(candidate_tagged_path: Path = None):
    candidate_tagged_path = candidate_tagged_path or CANDIDATE_TAGGED_PATH
    eval_ids = set(pd.read_csv(EVAL_PATH)["review_id"].astype(str))
    raw = pd.read_csv(RAW_PATH)
    raw["review_id"] = raw["review_id"].astype(str)
    eval_rows = raw[raw["review_id"].isin(eval_ids)]
    print(f"Re-tagging {len(eval_rows)} eval reviews with the updated prompt "
          f"(target: {len(eval_ids)})...")

    reviews = []
    for _, r in eval_rows.iterrows():
        reviews.append({
            "review_id": r["review_id"], "source": r["source"], "rating": int(r["rating"]),
            "date": r["date"], "text": str(r["text"]),
        })
    review_by_id = {r["review_id"]: r for r in reviews}

    taxonomy = load_taxonomy()
    valid_ids = valid_subcategory_ids(taxonomy)
    system_prompt, parent_lookup = build_system_prompt()
    print(f"Updated system prompt: {len(system_prompt):,} chars")

    result = tag_all(system_prompt, reviews, parent_lookup, valid_ids)
    retry_ids = set(result["missing_review_ids"]) | set(result["failed_review_ids"])
    if retry_ids:
        print(f"Retrying {len(retry_ids)} missing/failed individually...")
        retry_reviews = [review_by_id[rid] for rid in retry_ids if rid in review_by_id]
        retry_result = tag_all(system_prompt, retry_reviews, parent_lookup, valid_ids, batch_size=1, max_concurrency=4)
        result["tagged"].update(retry_result["tagged"])
        still_missing = set(retry_result["missing_review_ids"]) | set(retry_result["failed_review_ids"])
    else:
        still_missing = set()

    if still_missing:
        print(f"WARNING: {len(still_missing)} reviews still untagged after retry: {still_missing}")

    rows = []
    for r in reviews:
        tags = result["tagged"].get(r["review_id"])
        if tags is None:
            rows.append({"review_id": r["review_id"], "source": r["source"], "rating": r["rating"],
                         "date": r["date"], "text": r["text"], "parent_category_tags": "",
                         "subcategory_tags": "", "confidences": "", "tag_count": "", "status": "FAILED"})
            continue
        rows.append({
            "review_id": r["review_id"], "source": r["source"], "rating": r["rating"], "date": r["date"],
            "text": r["text"],
            "parent_category_tags": ";".join(t["parent_id"] for t in tags),
            "subcategory_tags": ";".join(t["subcategory_id"] for t in tags),
            "confidences": ";".join(t["confidence"] for t in tags),
            "tag_count": len(tags), "status": "OK",
        })

    with open(candidate_tagged_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} candidate predictions to {candidate_tagged_path}")
    return len(rows) - sum(1 for r in rows if r["status"] == "FAILED")


def compare(baseline: dict, candidate: dict):
    print("\n" + "=" * 70)
    print("BEFORE vs AFTER — headline metrics")
    print("=" * 70)
    for key, label in [
        ("sub_micro", "Subcategory micro-F1"), ("par_micro", "Parent micro-F1"),
    ]:
        b, c = baseline[key]["f1"], candidate[key]["f1"]
        print(f"{label:30s} {b:.3f} -> {c:.3f}  (delta {c - b:+.3f})")
    for key, label in [
        ("sub_macro_supported", "Subcategory macro-F1 (supported)"),
        ("par_macro_supported", "Parent macro-F1 (supported)"),
        ("exact_match_rate", "Exact-match rate (subcat)"),
        ("mean_jaccard", "Mean Jaccard"),
    ]:
        b, c = baseline[key], candidate[key]
        print(f"{label:34s} {b:.3f} -> {c:.3f}  (delta {c - b:+.3f})")
    b_other = baseline["agree_other"] / baseline["n_human_other"]
    c_other = candidate["agree_other"] / candidate["n_human_other"]
    print(f"{'Other/Ungrouped agreement':34s} {baseline['agree_other']}/{baseline['n_human_other']} ({b_other:.1%}) "
          f"-> {candidate['agree_other']}/{candidate['n_human_other']} ({c_other:.1%})")

    print("\n" + "=" * 70)
    print("Per-subcategory F1: BEFORE vs AFTER (every category, sorted by |delta| descending)")
    print("=" * 70)
    b_prf = baseline["sub_prf"].set_index("category")
    c_prf = candidate["sub_prf"].set_index("category")
    merged = b_prf[["support", "f1", "tp", "fp", "fn"]].join(
        c_prf[["support", "f1", "tp", "fp", "fn"]], lsuffix="_before", rsuffix="_after", how="outer"
    )
    merged["delta"] = merged["f1_after"] - merged["f1_before"]
    merged = merged.sort_values("delta", key=lambda s: s.abs(), ascending=False)
    for cat, r in merged.iterrows():
        flag = ""
        if pd.notna(r["delta"]) and r["delta"] < -0.05:
            flag = "  <-- REGRESSED"
        elif pd.notna(r["delta"]) and r["delta"] > 0.05:
            flag = "  <-- IMPROVED"
        f1b = "n/a" if pd.isna(r["f1_before"]) else f"{r['f1_before']:.3f}"
        f1a = "n/a" if pd.isna(r["f1_after"]) else f"{r['f1_after']:.3f}"
        d = "n/a" if pd.isna(r["delta"]) else f"{r['delta']:+.3f}"
        print(f"  {cat:32s} support(b={r['support_before']:.0f},a={r['support_after']:.0f})  "
              f"F1 {f1b} -> {f1a}  (delta {d}){flag}")

    print("\n" + "=" * 70)
    print("Borderline-pair confusion: BEFORE vs AFTER")
    print("=" * 70)
    b_pairs = baseline["pair_df"].set_index("pair")
    c_pairs = candidate["pair_df"].set_index("pair")
    for pair in b_pairs.index:
        b_swaps = b_pairs.loc[pair, "total_swaps"]
        c_swaps = c_pairs.loc[pair, "total_swaps"] if pair in c_pairs.index else "n/a"
        print(f"  {pair}: swaps {b_swaps} -> {c_swaps}")


def main(candidate_tagged_path: Path = None, candidate_report_path: Path = None, label: str = "candidate", show_baseline: bool = True):
    candidate_tagged_path = candidate_tagged_path or CANDIDATE_TAGGED_PATH
    candidate_report_path = candidate_report_path or CANDIDATE_REPORT_PATH

    n_ok = retag_eval_reviews(candidate_tagged_path)
    print(f"\n{n_ok} of 180 eval reviews successfully re-tagged ({label}).\n")

    baseline = None
    if show_baseline:
        print("Scoring BASELINE (original prompt, from data/tagged_reviews.csv)...")
        baseline = eval_tagger.main(tagged_path=eval_tagger.TAGGED_PATH, report_path=eval_tagger.REPORT_PATH,
                                     source_label="`data/tagged_reviews.csv` (original/baseline prompt)")

    print(f"\nScoring {label.upper()} (from {candidate_tagged_path.name})...")
    candidate = eval_tagger.main(tagged_path=candidate_tagged_path, report_path=candidate_report_path,
                                  source_label=f"`{candidate_tagged_path.name}` ({label}, eval-only re-tag)")

    if baseline:
        compare(baseline, candidate)

    return baseline, candidate


if __name__ == "__main__":
    main()
