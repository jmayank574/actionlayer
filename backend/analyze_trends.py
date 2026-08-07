"""Trend/velocity layer on top of the validated tagging output (ActionLayer v2,
step 4). Aggregates data/tagged_reviews.csv by time period x category x source,
computes rates (not raw counts), and flags categories whose recent rate has
moved meaningfully against a trailing baseline.

Critical handling: google_play has ~9 years of history; app_store only has
~9 months (Apple's public RSS feed exposes ~500 most-recent reviews only).
Every trend is computed PER SOURCE. A "combined" view exists ONLY for the
window where both sources have real coverage (Nov 2025 onward) -- never
mixing google_play's full history with app_store's recency-only data, which
would manufacture false spikes purely from source coverage, not real signal.

Does not modify data/tagged_reviews.csv, the tagging prompt, or the taxonomy.

Run with: python analyze_trends.py
"""

import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from tagging.taxonomy_loader import load_taxonomy, subcategory_to_parent_map, watch_category_ids

DATA_DIR = Path(__file__).parent / "data"
TAGGED_PATH = DATA_DIR / "tagged_reviews.csv"
TRENDS_OUT = DATA_DIR / "category_trends.csv"
REPORT_OUT = DATA_DIR / "trend_report.md"

# --- Thresholds (stated explicitly, used consistently) ---
MIN_BUCKET_VOLUME = 30      # minimum reviews in a time bucket for its rate to be "reliable" for the descriptive series
MIN_BASELINE_VOLUME = 50    # minimum total reviews in a source's baseline window, else skip that source entirely
MIN_TAG_COUNT_RECENT = 5    # minimum occurrences of a tag in the recent window to treat a rate change as signal, not noise
SPIKE_RELATIVE = 1.5        # recent rate >= 1.5x baseline rate
SPIKE_ABSOLUTE_PP = 2.0     # AND at least +2 percentage points
DECLINE_RELATIVE = 1 / 1.5  # recent rate <= (1/1.5)x baseline rate
DECLINE_ABSOLUTE_PP = 2.0   # AND at least -2 percentage points
RECENT_WINDOW_MONTHS = 3
BASELINE_WINDOW_MONTHS = 12


def load_reviews() -> pd.DataFrame:
    df = pd.read_csv(TAGGED_PATH)
    df["date_parsed"] = pd.to_datetime(df["date"], format="mixed", utc=True).dt.tz_localize(None)
    df["month"] = df["date_parsed"].dt.to_period("M")
    df["parent_category_tags"] = df["parent_category_tags"].fillna("")
    df["subcategory_tags"] = df["subcategory_tags"].fillna("")
    return df


def explode_tags(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (review_id, category_id, level)."""
    rows = []
    for _, r in df.iterrows():
        parents = [p for p in r["parent_category_tags"].split(";") if p]
        subs = [s for s in r["subcategory_tags"].split(";") if s]
        for p in set(parents):
            rows.append({"review_id": r["review_id"], "source": r["source"], "month": r["month"],
                         "date_parsed": r["date_parsed"], "level": "parent", "category_id": p})
        for s in set(subs):
            rows.append({"review_id": r["review_id"], "source": r["source"], "month": r["month"],
                         "date_parsed": r["date_parsed"], "level": "subcategory", "category_id": s})
    return pd.DataFrame(rows)


def build_adaptive_buckets(monthly_totals: pd.Series, min_volume: int) -> list[dict]:
    """Greedily merges consecutive months (in order) until each bucket has
    >= min_volume reviews. Any leftover under-threshold tail is merged into
    the previous bucket rather than left as an unreliable orphan. Returns a
    list of {months: [Period...], label: str, period_type: 'month'|'multi_month'}."""
    months = sorted(monthly_totals.index)
    buckets = []
    current_months = []
    current_total = 0
    for m in months:
        current_months.append(m)
        current_total += monthly_totals[m]
        if current_total >= min_volume:
            buckets.append(list(current_months))
            current_months = []
            current_total = 0
    if current_months:
        if buckets:
            buckets[-1].extend(current_months)
        else:
            buckets.append(current_months)

    result = []
    for b in buckets:
        if len(b) == 1:
            label, ptype = str(b[0]), "month"
        else:
            label, ptype = f"{b[0]}_to_{b[-1]}", "multi_month"
        result.append({"months": b, "label": label, "period_type": ptype})
    return result


def compute_descriptive_series(exploded: pd.DataFrame, all_reviews: pd.DataFrame, categories: list[str],
                                scopes: dict[str, dict] | None = None) -> pd.DataFrame:
    """Per scope, per adaptive bucket, per category: tag_count / total_reviews / rate_pct.

    scopes: {scope_name: {"sources": [...], "min_month": Period|None}}. Defaults to the two
    single-source scopes. min_month restricts a scope to periods >= that month -- used by
    combined_overlap so it never buckets in google_play-only history before app_store existed
    (the exact mixing this whole analysis exists to avoid)."""
    if scopes is None:
        scopes = {
            "google_play": {"sources": ["google_play"], "min_month": None},
            "app_store": {"sources": ["app_store"], "min_month": None},
        }

    rows = []
    for scope_name, cfg in scopes.items():
        scope_reviews = all_reviews[all_reviews["source"].isin(cfg["sources"])]
        if cfg.get("min_month") is not None:
            scope_reviews = scope_reviews[scope_reviews["month"] >= cfg["min_month"]]
        monthly_totals = scope_reviews.groupby("month").size()
        buckets = build_adaptive_buckets(monthly_totals, MIN_BUCKET_VOLUME)

        scope_exploded = exploded[exploded["source"].isin(cfg["sources"])]
        if cfg.get("min_month") is not None:
            scope_exploded = scope_exploded[scope_exploded["month"] >= cfg["min_month"]]

        for b in buckets:
            month_set = set(b["months"])
            bucket_total = int(monthly_totals[monthly_totals.index.isin(month_set)].sum())
            bucket_exploded = scope_exploded[scope_exploded["month"].isin(month_set)]
            counts = bucket_exploded.groupby("category_id")["review_id"].nunique()

            for cat in categories:
                tag_count = int(counts.get(cat, 0))
                rate = (tag_count / bucket_total * 100) if bucket_total else float("nan")
                rows.append({
                    "period": b["label"], "period_type": b["period_type"],
                    "period_start": str(min(b["months"])), "period_end": str(max(b["months"])),
                    "source": scope_name, "category_id": cat,
                    "tag_count": tag_count, "total_reviews": bucket_total,
                    "rate_pct": round(rate, 3) if bucket_total else None,
                    "adequate_volume": bucket_total >= MIN_BUCKET_VOLUME,
                })
    return pd.DataFrame(rows)


def window_rate(exploded: pd.DataFrame, all_reviews: pd.DataFrame, source_filter, start, end, cat: str) -> tuple[int, int, float]:
    """source_filter: a boolean mask column value list, e.g. ['google_play'] or ['google_play','app_store']."""
    mask_all = all_reviews["source"].isin(source_filter) & (all_reviews["date_parsed"] >= start) & (all_reviews["date_parsed"] < end)
    total = int(mask_all.sum())
    mask_exp = exploded["source"].isin(source_filter) & (exploded["date_parsed"] >= start) & (exploded["date_parsed"] < end) & (exploded["category_id"] == cat)
    count = int(exploded.loc[mask_exp, "review_id"].nunique())
    rate = (count / total * 100) if total else float("nan")
    return count, total, rate


def classify(recent_count, recent_total, recent_rate, base_count, base_total, base_rate) -> dict:
    if recent_total < 1 or base_total < MIN_BASELINE_VOLUME:
        return {"verdict": "insufficient_baseline_volume", "flagged_spike": False, "flagged_decline": False, "emerging": False}
    if recent_count < MIN_TAG_COUNT_RECENT:
        return {"verdict": "insufficient_recent_occurrences", "flagged_spike": False, "flagged_decline": False, "emerging": False}

    if base_count == 0:
        return {"verdict": "emerging_new_category", "flagged_spike": True, "flagged_decline": False, "emerging": True}

    ratio = recent_rate / base_rate if base_rate else float("inf")
    pp_delta = recent_rate - base_rate

    if ratio >= SPIKE_RELATIVE and pp_delta >= SPIKE_ABSOLUTE_PP:
        return {"verdict": "spike", "flagged_spike": True, "flagged_decline": False, "emerging": False}
    if ratio <= DECLINE_RELATIVE and pp_delta <= -DECLINE_ABSOLUTE_PP:
        return {"verdict": "decline", "flagged_spike": False, "flagged_decline": True, "emerging": False}
    return {"verdict": "stable", "flagged_spike": False, "flagged_decline": False, "emerging": False}


def main():
    print("Loading tagged_reviews.csv...")
    df = load_reviews()
    exploded = explode_tags(df)

    taxonomy = load_taxonomy()
    parent_lookup = subcategory_to_parent_map(taxonomy)
    watch_ids = watch_category_ids(taxonomy)
    all_subcats = sorted(parent_lookup.keys())
    all_parents = sorted({c["id"] for c in taxonomy["categories"]})
    all_categories = all_parents + all_subcats

    # Exclude the current partial month from all analysis.
    max_month = df["month"].max()
    current_month_start = max_month.to_timestamp()
    print(f"Excluding current partial month ({max_month}) from trend analysis "
          f"({(df['month'] == max_month).sum()} reviews excluded as incomplete).")
    df_complete = df[df["month"] < max_month].copy()
    exploded_complete = exploded[exploded["month"] < max_month].copy()

    app_store_min_month = df_complete.loc[df_complete["source"] == "app_store", "month"].min()

    print("\nBuilding descriptive time series (adaptive monthly/multi-month buckets, "
          f"min {MIN_BUCKET_VOLUME} reviews/bucket)...")
    descriptive_scopes = {
        "google_play": {"sources": ["google_play"], "min_month": None},
        "app_store": {"sources": ["app_store"], "min_month": None},
        # combined_overlap: both sources pooled, but only from the month app_store
        # actually starts existing -- never buckets google_play-only history in with it.
        "combined_overlap": {"sources": ["google_play", "app_store"], "min_month": app_store_min_month},
    }
    descriptive = compute_descriptive_series(exploded_complete, df_complete, all_categories, descriptive_scopes)
    print(f"  {len(descriptive)} (period x scope x category) rows")

    # --- Recent / baseline windows ---
    recent_end = current_month_start
    recent_start = (recent_end - pd.DateOffset(months=RECENT_WINDOW_MONTHS))
    print(f"\nRecent window: [{recent_start.date()}, {recent_end.date()}) ({RECENT_WINDOW_MONTHS} complete months)")

    scopes = {}
    for source_name, sources in [("google_play", ["google_play"]), ("app_store", ["app_store"])]:
        src_min_date = df_complete.loc[df_complete["source"] == source_name, "date_parsed"].min()
        baseline_start_ideal = recent_start - pd.DateOffset(months=BASELINE_WINDOW_MONTHS)
        baseline_start = max(baseline_start_ideal, src_min_date) if pd.notna(src_min_date) else baseline_start_ideal
        scopes[source_name] = {"sources": sources, "baseline_start": baseline_start, "baseline_end": recent_start}

    # combined_overlap: both sources pooled, restricted to the window both actually cover
    app_store_min = df_complete.loc[df_complete["source"] == "app_store", "date_parsed"].min()
    combined_baseline_start = max(app_store_min, recent_start - pd.DateOffset(months=BASELINE_WINDOW_MONTHS))
    scopes["combined_overlap"] = {"sources": ["google_play", "app_store"], "baseline_start": combined_baseline_start, "baseline_end": recent_start}

    for name, s in scopes.items():
        months_of_baseline = (s["baseline_end"] - s["baseline_start"]).days / 30.44
        print(f"  scope={name}: baseline [{s['baseline_start'].date()}, {s['baseline_end'].date()}) "
              f"(~{months_of_baseline:.1f} months)")

    # --- Recent vs baseline verdicts per scope x category ---
    verdicts = []
    for scope_name, s in scopes.items():
        for cat in all_categories:
            rc, rt, rr = window_rate(exploded_complete, df_complete, s["sources"], recent_start, recent_end, cat)
            bc, bt, br = window_rate(exploded_complete, df_complete, s["sources"], s["baseline_start"], s["baseline_end"], cat)
            v = classify(rc, rt, rr, bc, bt, br)
            level = "parent" if cat in all_parents else "subcategory"
            verdicts.append({
                "scope": scope_name, "level": level, "category_id": cat,
                "recent_count": rc, "recent_total": rt, "recent_rate_pct": round(rr, 3) if rt else None,
                "baseline_count": bc, "baseline_total": bt, "baseline_rate_pct": round(br, 3) if bt else None,
                "pp_delta": round(rr - br, 3) if rt and bt and pd.notna(rr) and pd.notna(br) else None,
                "ratio": round(rr / br, 2) if bt and br and rt else None,
                **v,
            })
    verdicts_df = pd.DataFrame(verdicts)

    # --- Merge verdicts onto the descriptive series for recent-window rows ---
    descriptive["in_recent_window"] = False
    descriptive["scope"] = descriptive["source"]
    descriptive["rolling_baseline_rate_pct"] = None
    descriptive["flagged_spike"] = False
    descriptive["flagged_decline"] = False
    descriptive["verdict"] = None

    for idx, row in descriptive.iterrows():
        period_end = pd.Period(row["period_end"], freq="M").end_time
        if period_end >= recent_start and row["source"] in ("google_play", "app_store", "combined_overlap"):
            v = verdicts_df[(verdicts_df["scope"] == row["source"]) & (verdicts_df["category_id"] == row["category_id"])]
            if len(v):
                vrow = v.iloc[0]
                descriptive.at[idx, "in_recent_window"] = True
                descriptive.at[idx, "rolling_baseline_rate_pct"] = vrow["baseline_rate_pct"]
                descriptive.at[idx, "flagged_spike"] = vrow["flagged_spike"]
                descriptive.at[idx, "flagged_decline"] = vrow["flagged_decline"]
                descriptive.at[idx, "verdict"] = vrow["verdict"]

    descriptive.to_csv(TRENDS_OUT, index=False)
    print(f"\nWrote {len(descriptive)} rows to {TRENDS_OUT}")

    verdicts_df.to_csv(DATA_DIR / "category_trend_verdicts.csv", index=False)
    print(f"Wrote {len(verdicts_df)} scope x category verdicts to data/category_trend_verdicts.csv")

    return df, exploded_complete, verdicts_df, descriptive, watch_ids, all_parents, recent_start, recent_end, scopes


if __name__ == "__main__":
    main()
