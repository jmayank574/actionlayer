"""Stratified sample for bottom-up taxonomy design (ActionLayer v2, step 2).

Pulls a fixed, reproducible sample from data/whoop_reviews_raw.csv, stratified
by source x rating x time period so no single dimension (source, star rating,
or recency) dominates what gets read. Writes data/taxonomy_sample.csv.

This does not modify the raw dataset and assigns no categories — it only
selects which real reviews get read for open coding.

Run with: python sample_for_taxonomy.py
"""

import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent / "data"
SRC_PATH = DATA_DIR / "whoop_reviews_raw.csv"
OUT_PATH = DATA_DIR / "taxonomy_sample.csv"

SEED = 42
GOOGLE_PLAY_TARGET = 115
APP_STORE_TARGET = 65
N_TIME_BUCKETS = 3


def stratified_sample(df: pd.DataFrame, rating_col: str, time_col: str | None, target: int, n_time_buckets: int) -> pd.DataFrame:
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
                picked.append(bucket_df.sample(n=n, random_state=SEED))
        else:
            n = min(per_rating_target, len(rating_df))
            picked.append(rating_df.sample(n=n, random_state=SEED))

    result = pd.concat(picked).drop_duplicates(subset=["review_id", "text"])

    # Top up or trim to land close to the target count.
    shortfall = target - len(result)
    if shortfall > 0:
        remaining = df.drop(result.index, errors="ignore")
        if len(remaining) > 0:
            topup = remaining.sample(n=min(shortfall, len(remaining)), random_state=SEED)
            result = pd.concat([result, topup])
    elif shortfall < 0:
        result = result.sample(n=target, random_state=SEED)

    return result


def main():
    df = pd.read_csv(SRC_PATH)
    df["date_parsed"] = pd.to_datetime(df["date"], format="mixed", utc=True)

    gp = df[df["source"] == "google_play"]
    as_ = df[df["source"] == "app_store"]

    gp_sample = stratified_sample(gp, "rating", "date_parsed", GOOGLE_PLAY_TARGET, N_TIME_BUCKETS)
    as_sample = stratified_sample(as_, "rating", "date_parsed", APP_STORE_TARGET, N_TIME_BUCKETS)

    sample = pd.concat([gp_sample, as_sample]).drop(columns=["date_parsed"])
    sample = sample.sample(frac=1, random_state=SEED).reset_index(drop=True)
    sample.insert(0, "sample_id", range(1, len(sample) + 1))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUT_PATH, index=False)

    print(f"Wrote {len(sample)} sampled reviews to {OUT_PATH}")
    print(sample.groupby(["source", "rating"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()
