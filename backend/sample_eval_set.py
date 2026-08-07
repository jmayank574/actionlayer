"""Held-out evaluation sample (ActionLayer v2, step 2.5).

Draws a second stratified sample from data/whoop_reviews_raw.csv, disjoint
from data/taxonomy_sample.csv (the 180 reviews used to BUILD the taxonomy),
for honest evaluation of the step-3 tagger against reviews the taxonomy's
boundaries were never written to fit.

This script does not label anything — it only selects rows and writes blank
columns for manual labeling. Same stratification method as
sample_for_taxonomy.py, different random seed.

Run with: python sample_eval_set.py
"""

import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent / "data"
RAW_PATH = DATA_DIR / "whoop_reviews_raw.csv"
ORIGINAL_SAMPLE_PATH = DATA_DIR / "taxonomy_sample.csv"
OUT_PATH = DATA_DIR / "eval_sample.csv"

SEED = 101  # deliberately different from sample_for_taxonomy.py's SEED = 42
GOOGLE_PLAY_TARGET = 115
APP_STORE_TARGET = 65
N_TIME_BUCKETS = 3

LABEL_COLUMNS = ["parent_category_tags", "subcategory_tags", "notes"]


def stratified_sample(df: pd.DataFrame, rating_col: str, time_col: str | None, target: int, n_time_buckets: int, seed: int) -> pd.DataFrame:
    """Same method as sample_for_taxonomy.py's stratified_sample, parameterized on seed."""
    ratings = sorted(df[rating_col].dropna().unique())
    per_rating_target = max(1, round(target / len(ratings)))

    picked = []
    for rating in ratings:
        rating_df = df[df[rating_col] == rating]
        if time_col is not None and rating_df[time_col].nunique() > 1:
            buckets = pd.qcut(rating_df[time_col].rank(method="first"), q=min(n_time_buckets, len(rating_df)), labels=False)
            per_bucket_target = max(1, round(per_rating_target / n_time_buckets))
            for b in sorted(buckets.unique()):
                bucket_df = rating_df[buckets == b]
                n = min(per_bucket_target, len(bucket_df))
                if n > 0:
                    picked.append(bucket_df.sample(n=n, random_state=seed))
        else:
            n = min(per_rating_target, len(rating_df))
            if n > 0:
                picked.append(rating_df.sample(n=n, random_state=seed))

    result = pd.concat(picked).drop_duplicates(subset=["review_id", "text"])

    shortfall = target - len(result)
    if shortfall > 0:
        remaining = df.drop(result.index, errors="ignore")
        if len(remaining) > 0:
            topup = remaining.sample(n=min(shortfall, len(remaining)), random_state=seed)
            result = pd.concat([result, topup])
    elif shortfall < 0:
        result = result.sample(n=target, random_state=seed)

    return result


def main():
    raw = pd.read_csv(RAW_PATH)
    original = pd.read_csv(ORIGINAL_SAMPLE_PATH)

    print(f"Full raw dataset: {len(raw)} reviews")
    print(f"Original taxonomy-building sample: {len(original)} reviews")
    print()

    # --- Overlap check, shown explicitly, before any sampling happens ---
    original_ids = set(original["review_id"])
    original_texts = set(original["text"])

    ids_found_in_raw = raw["review_id"].isin(original_ids).sum()
    print(f"Overlap check 1 (review_id): {ids_found_in_raw} of {len(original_ids)} "
          f"original review_ids appear in the raw dataset (expected: all {len(original_ids)}, "
          f"confirming the ids are stable and traceable back to source).")

    pool_after_id_exclusion = raw[~raw["review_id"].isin(original_ids)]
    print(f"After excluding by review_id: {len(raw)} -> {len(pool_after_id_exclusion)} "
          f"({len(raw) - len(pool_after_id_exclusion)} removed).")

    # Backup exclusion by exact text match, in case review_id has any reuse/duplication.
    remaining_text_overlap = pool_after_id_exclusion["text"].isin(original_texts).sum()
    print(f"Overlap check 2 (exact text, backup): {remaining_text_overlap} rows in the "
          f"id-filtered pool still match an original review's exact text "
          f"(expected: 0 if review_id was a sufficient key on its own).")

    pool = pool_after_id_exclusion[~pool_after_id_exclusion["text"].isin(original_texts)]
    print(f"After excluding by text (backup): {len(pool_after_id_exclusion)} -> {len(pool)} "
          f"({len(pool_after_id_exclusion) - len(pool)} additional rows removed).")
    print()

    assert pool["review_id"].isin(original_ids).sum() == 0
    assert pool["text"].isin(original_texts).sum() == 0
    print("Confirmed: candidate pool has zero overlap with the original 180-review sample "
          "by both review_id and exact text.")
    print()

    # --- Stratified sampling from the disjoint pool, new seed ---
    pool = pool.copy()
    pool["date_parsed"] = pd.to_datetime(pool["date"], format="mixed", utc=True)

    gp = pool[pool["source"] == "google_play"]
    as_ = pool[pool["source"] == "app_store"]

    gp_sample = stratified_sample(gp, "rating", "date_parsed", GOOGLE_PLAY_TARGET, N_TIME_BUCKETS, SEED)
    as_sample = stratified_sample(as_, "rating", "date_parsed", APP_STORE_TARGET, N_TIME_BUCKETS, SEED)

    sample = pd.concat([gp_sample, as_sample]).drop(columns=["date_parsed"])
    sample = sample.sample(frac=1, random_state=SEED).reset_index(drop=True)
    sample.insert(0, "eval_id", range(1, len(sample) + 1))

    # Final re-verification post-sampling, not just on the pre-sample pool.
    final_id_overlap = sample["review_id"].isin(original_ids).sum()
    final_text_overlap = sample["text"].isin(original_texts).sum()
    assert final_id_overlap == 0 and final_text_overlap == 0
    print(f"Post-sampling re-check on the final {len(sample)}-row eval sample: "
          f"{final_id_overlap} review_id overlaps, {final_text_overlap} text overlaps with the "
          f"original 180 — confirmed disjoint.")
    print()

    for col in LABEL_COLUMNS:
        sample[col] = ""

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(sample)} unlabeled eval reviews to {OUT_PATH}")
    print(sample.groupby(["source", "rating"]).size().unstack(fill_value=0))

    return {
        "raw_total": len(raw),
        "original_total": len(original),
        "ids_found_in_raw": int(ids_found_in_raw),
        "pool_after_id_exclusion": len(pool_after_id_exclusion),
        "remaining_text_overlap": int(remaining_text_overlap),
        "final_pool_size": len(pool),
        "eval_sample_size": len(sample),
        "seed": SEED,
    }


if __name__ == "__main__":
    main()
