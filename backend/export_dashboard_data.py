"""Exports already-computed pipeline outputs into frontend-consumable JSON
(ActionLayer v2, dashboard scaffold). Reshapes data/tagged_reviews.csv,
data/category_trends.csv, and data/category_trend_verdicts.csv — recomputes
nothing, reads backend/data/ only, never writes to it.

Run with: python export_dashboard_data.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from tagging.taxonomy_loader import load_taxonomy

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent.parent / "frontend" / "public" / "data" / "whoop"

REVIEW_SAMPLE_CAP = 30  # most-recent reviews exported per category, for drill-down


def category_meta(taxonomy: dict) -> dict:
    """category_id -> {name, level, parent_id (subcats only), watch_category, watch_reason}."""
    meta = {}
    for cat in taxonomy["categories"]:
        meta[cat["id"]] = {
            "name": cat["name"], "level": "parent", "parent_id": None,
            "watch_category": bool(cat.get("watch_category")),
            "watch_reason": cat.get("watch_reason", "").strip() or None,
        }
        for sub in cat["subcategories"]:
            meta[sub["id"]] = {
                "name": sub["name"], "level": "subcategory", "parent_id": cat["id"],
                # a subcategory inherits its parent's watch status -- same stakes, finer grain
                "watch_category": bool(cat.get("watch_category")),
                "watch_reason": cat.get("watch_reason", "").strip() or None,
            }
    return meta


def build_snapshot(tagged: pd.DataFrame, taxonomy: dict, meta: dict) -> dict:
    total = len(tagged)
    other_count = int((tagged["tag_count"].fillna(0) == 0).sum())

    def counts_for(col):
        c = {}
        for tags in tagged[col].fillna(""):
            for t in tags.split(";"):
                if t:
                    c[t] = c.get(t, 0) + 1
        return c

    sub_counts = counts_for("subcategory_tags")
    par_counts = counts_for("parent_category_tags")

    parents = []
    for cat in taxonomy["categories"]:
        pid = cat["id"]
        pcount = par_counts.get(pid, 0)
        subs = []
        for sub in cat["subcategories"]:
            sid = sub["id"]
            scount = sub_counts.get(sid, 0)
            subs.append({
                "id": sid, "name": sub["name"],
                "count": scount, "rate_pct": round(scount / total * 100, 3) if total else None,
                "watch_category": meta[sid]["watch_category"],
            })
        parents.append({
            "id": pid, "name": cat["name"],
            "count": pcount, "rate_pct": round(pcount / total * 100, 3) if total else None,
            "watch_category": meta[pid]["watch_category"],
            "watch_reason": meta[pid]["watch_reason"],
            "subcategories": subs,
        })

    return {
        "product_id": "whoop",
        "total_reviews": total,
        "other_ungrouped": {"count": other_count, "rate_pct": round(other_count / total * 100, 3) if total else None},
        "parents": parents,
    }


def build_trends_timeseries(trends: pd.DataFrame, meta: dict) -> dict:
    """Nested by scope -> category_id -> [ {period, rate_pct, tag_count, total_reviews,
    period_type, adequate_volume, in_recent_window, flagged_spike, flagged_decline}, ... ]
    ordered chronologically. scope here is the source column (google_play/app_store) --
    combined_overlap isn't in the descriptive series, only in the verdicts (see trend_verdicts.json)."""
    trends = trends.sort_values("period_start")
    out: dict[str, dict[str, list]] = {}
    for _, r in trends.iterrows():
        scope = r["source"]
        cat = r["category_id"]
        out.setdefault(scope, {}).setdefault(cat, []).append({
            "period": r["period"], "period_type": r["period_type"],
            "period_start": r["period_start"], "period_end": r["period_end"],
            "rate_pct": None if pd.isna(r["rate_pct"]) else r["rate_pct"],
            "tag_count": int(r["tag_count"]), "total_reviews": int(r["total_reviews"]),
            "adequate_volume": bool(r["adequate_volume"]),
            "in_recent_window": bool(r["in_recent_window"]),
            "flagged_spike": bool(r["flagged_spike"]),
            "flagged_decline": bool(r["flagged_decline"]),
        })
    return out


def build_trend_verdicts(verdicts: pd.DataFrame, meta: dict) -> list[dict]:
    records = []
    for _, r in verdicts.iterrows():
        cat = r["category_id"]
        records.append({
            "scope": r["scope"], "level": r["level"], "category_id": cat,
            "category_name": meta.get(cat, {}).get("name", cat),
            "watch_category": meta.get(cat, {}).get("watch_category", False),
            "recent_count": int(r["recent_count"]), "recent_total": int(r["recent_total"]),
            "recent_rate_pct": None if pd.isna(r["recent_rate_pct"]) else r["recent_rate_pct"],
            "baseline_count": int(r["baseline_count"]), "baseline_total": int(r["baseline_total"]),
            "baseline_rate_pct": None if pd.isna(r["baseline_rate_pct"]) else r["baseline_rate_pct"],
            "pp_delta": None if pd.isna(r["pp_delta"]) else r["pp_delta"],
            "ratio": None if pd.isna(r["ratio"]) else r["ratio"],
            "verdict": r["verdict"],
            "flagged_spike": bool(r["flagged_spike"]), "flagged_decline": bool(r["flagged_decline"]),
            "emerging": bool(r["emerging"]),
        })
    return records


def build_review_samples(tagged: pd.DataFrame, all_category_ids: list[str]) -> dict:
    tagged = tagged.copy()
    tagged["date_parsed"] = pd.to_datetime(tagged["date"], format="mixed", utc=True)
    tagged = tagged.sort_values("date_parsed", ascending=False)

    samples = {}
    for cat in all_category_ids:
        mask = (
            tagged["subcategory_tags"].fillna("").str.contains(rf"(?:^|;){cat}(?:;|$)", regex=True)
            | tagged["parent_category_tags"].fillna("").str.contains(rf"(?:^|;){cat}(?:;|$)", regex=True)
        )
        rows = tagged[mask].head(REVIEW_SAMPLE_CAP)
        samples[cat] = [
            {
                "review_id": row["review_id"], "source": row["source"], "rating": int(row["rating"]),
                "date": row["date"], "text": row["text"],
                "subcategory_tags": [t for t in str(row["subcategory_tags"] or "").split(";") if t],
            }
            for _, row in rows.iterrows()
        ]
    return samples


MIN_QUOTE_WORDS = 12
MAX_QUOTE_WORDS = 55
QUOTES_PER_SUBCATEGORY = 3
CARD_QUOTE_COUNT = 2
TOP_DRIVERS_COUNT = 3
MULTI_LABEL_NOTE_THRESHOLD_PP = 1.0  # parent_rate vs subcategory-sum divergence worth calling out
INSIGHT_FEED_SCOPE = "combined_overlap"  # both sources pooled (Nov 2025 onward, the real
                                          # overlap window -- see analyze_trends.py) so the
                                          # primary feed reflects total review volume, not just
                                          # one source. google_play-only and app_store-only
                                          # verdicts are still fully available in the Explore
                                          # view's scope selector for anyone who wants the
                                          # single-source breakdown.

# Zone A ("Priority Insights") -- what someone should act on this week. Needs
# real confidence, not just measurability, so its volume floor is well above
# MIN_TAG_COUNT_RECENT (5, analyze_trends.py's "is this even measurable" bar
# used everywhere else). 15 is chosen as a round number meaningfully past the
# noise floor while still reachable in practice: even WHOOP's largest
# categories only produce a few hundred tagged reviews in a 3-month window,
# so demanding e.g. 50+ recent mentions would leave Zone A empty most
# periods. Tune this constant directly if it proves too strict/loose.
ZONE_A_MIN_VOLUME = 15
ZONE_A_MAX_CARDS = 6

PRIORITY_SCORE_FORMULA = (
    "priority_score = recent_count * abs(pp_delta) -- rewards both real volume and real "
    "movement together. A 10pp swing on 5 reviews (score 50) ranks below a 3pp swing on 40 "
    "reviews (score 120), matching the product intuition that a moderate move backed by a lot "
    "of real signal deserves more attention than a dramatic move on a handful of reviews. "
    "Tunable: swap in recent_count**0.5 * abs(pp_delta) to dampen volume's influence, or "
    "multiply by baseline_total if categories with a thin baseline should also be discounted."
)


def priority_score(recent_count: int, pp_delta: float | None) -> float:
    return abs(pp_delta or 0) * recent_count


def derive_recent_window(trends: pd.DataFrame, scope: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Reads the recent-window boundary back out of category_trends.csv's own
    in_recent_window flag (set by analyze_trends.py) rather than recomputing
    window math independently -- reuse, don't reinvent."""
    scoped = trends[(trends["source"] == scope) & (trends["in_recent_window"])]
    start = pd.Period(scoped["period_start"].min(), freq="M").start_time
    last_month = pd.Period(scoped["period_end"].max(), freq="M")
    end = (last_month + 1).start_time  # exclusive upper bound, matches analyze_trends.py's recent_end
    return start, end


def select_quotes(tagged: pd.DataFrame, category_id: str, start: pd.Timestamp, end: pd.Timestamp, n: int) -> list[dict]:
    mask = (
        (tagged["date_parsed"] >= start) & (tagged["date_parsed"] < end)
        & (
            tagged["subcategory_tags"].fillna("").str.contains(rf"(?:^|;){category_id}(?:;|$)", regex=True)
            | tagged["parent_category_tags"].fillna("").str.contains(rf"(?:^|;){category_id}(?:;|$)", regex=True)
        )
    )
    candidates = tagged[mask].sort_values("date_parsed", ascending=False)
    word_counts = candidates["text"].str.split().str.len()
    preferred = candidates[(word_counts >= MIN_QUOTE_WORDS) & (word_counts <= MAX_QUOTE_WORDS)]
    chosen = preferred.head(n)
    if len(chosen) < n:
        # fall back to whatever's available (still real, just outside the preferred length band)
        remaining = candidates[~candidates.index.isin(chosen.index)].head(n - len(chosen))
        chosen = pd.concat([chosen, remaining])
    return [
        {"review_id": r["review_id"], "source": r["source"], "rating": int(r["rating"]),
         "date": r["date"], "text": r["text"]}
        for _, r in chosen.iterrows()
    ]


def badge_status(is_watch: bool, flagged_spike: bool, flagged_decline: bool) -> str:
    # Watch-category membership takes precedence over spike/decline: a watch
    # category's badge reflects that it's being monitored for stakes, not
    # magnitude/direction -- consistent with how watch categories are treated
    # everywhere else in this project (visible regardless of whether they
    # moved). A non-watch category's badge is a direct read of its flag --
    # this is only semantically safe because every non-watch flagged parent
    # in this dataset (app_stability, hardware_wearability, feature_requests)
    # has exclusively complaint-shaped subcategories, so "spike = more
    # complaints = needs attention" and "decline = fewer complaints =
    # improving" both hold. A category mixing praise and complaint
    # subcategories (like ai_coach) would need per-subcategory sentiment to
    # do this mechanically -- it's a watch category here, so the ambiguity
    # never has to be resolved by the badge; the narrative paragraph carries it.
    if is_watch:
        return "watching"
    if flagged_spike:
        return "needs_attention"
    if flagged_decline:
        return "improving"
    return "stable"


def card_title(name: str, status: str, ratio: float | None, recent_rate: float | None) -> str:
    if status == "watching":
        if ratio is not None and ratio >= 1.1:
            return f"{name}: mentions up {ratio:.1f}x this period"
        if ratio is not None and ratio <= 0.9:
            return f"{name}: mentions down this period"
        return f"{name}: steady, still monitoring"
    if status == "needs_attention":
        return f"{name} complaints are rising"
    if status == "improving":
        return f"{name} complaints are easing"
    return f"{name}: no significant change"


def card_narrative(name: str, status: str, recent_rate: float, baseline_rate: float, ratio: float | None,
                    recent_count: int, window_label: str, top_sub_name: str | None, top_sub_pp: float | None) -> str:
    # Kept to 1-2 plain sentences, matching the reference card style -- the
    # multi-label reconciliation note, watch-category stakes, and subcategory
    # driver breakdown are deliberately NOT folded in here anymore; they live
    # in the card's (i) tooltip and expandable driver list instead, so the
    # primary paragraph stays short.
    if status == "stable" or ratio is None:
        return (
            f"{name} shows no significant change this period — {recent_rate:.1f}% of reviews "
            f"({recent_count}) over {window_label}, close to its {baseline_rate:.1f}% baseline."
        )
    direction = "rose" if recent_rate >= baseline_rate else "fell"
    parts = [
        f"{name} {direction} from {baseline_rate:.1f}% to {recent_rate:.1f}% of reviews over "
        f"{window_label} — {ratio:.1f}x baseline. {recent_count} reviews now reference this"
    ]
    if top_sub_name:
        parts.append(f", primarily driven by {top_sub_name} ({top_sub_pp:+.1f}pp)")
    return "".join(parts) + "."


def build_insight_feed(tagged: pd.DataFrame, verdicts: pd.DataFrame, trends: pd.DataFrame, meta: dict,
                        scope: str = INSIGHT_FEED_SCOPE) -> dict:
    tagged = tagged.copy()
    if "date_parsed" not in tagged.columns:
        tagged["date_parsed"] = pd.to_datetime(tagged["date"], format="mixed", utc=True).dt.tz_localize(None)
    win_start, win_end = derive_recent_window(trends, scope)
    window_label = f"{win_start.strftime('%b %Y')}–{(win_end - pd.Timedelta(days=1)).strftime('%b %Y')}"

    scoped = verdicts[verdicts["scope"] == scope]
    parent_rows = scoped[scoped["level"] == "parent"]

    watch_parent_ids = [cid for cid, m in meta.items() if m["level"] == "parent" and m["watch_category"]]
    flagged_parent_ids = parent_rows[parent_rows["flagged_spike"] | parent_rows["flagged_decline"]]["category_id"].tolist()
    # Every candidate that could appear in EITHER zone gets a full card built
    # (watch categories always; flagged movers regardless of whether they'll
    # clear Zone A's volume floor) -- zone membership is decided afterward
    # from this one card set, so a category built once can legitimately
    # appear in both zones without being built twice.
    final_ids = list(dict.fromkeys(watch_parent_ids + flagged_parent_ids))

    cards = []
    for pid in final_ids:
        prow = parent_rows[parent_rows["category_id"] == pid]
        if len(prow) == 0:
            continue
        prow = prow.iloc[0]
        is_watch = pid in watch_parent_ids
        status = badge_status(is_watch, bool(prow["flagged_spike"]), bool(prow["flagged_decline"]))

        sub_ids = [cid for cid, m in meta.items() if m["parent_id"] == pid]
        sub_rows = scoped[(scoped["level"] == "subcategory") & (scoped["category_id"].isin(sub_ids))].copy()
        sub_rows["abs_pp"] = sub_rows["pp_delta"].abs()
        sub_rows = sub_rows.sort_values("abs_pp", ascending=False)

        parent_recent_rate = prow["recent_rate_pct"]
        sub_sum = sub_rows["recent_rate_pct"].sum() if len(sub_rows) else 0.0
        divergence = (sub_sum - parent_recent_rate) if pd.notna(parent_recent_rate) else 0.0
        multi_label_note = None
        if abs(divergence) >= MULTI_LABEL_NOTE_THRESHOLD_PP:
            multi_label_note = (
                f"Some reviews touch more than one issue in this category, so subcategory shares "
                f"add up to {sub_sum:.1f}% even though {parent_recent_rate:.1f}% of reviews are "
                f"affected overall."
            )

        top_drivers = []
        for _, srow in sub_rows.head(TOP_DRIVERS_COUNT).iterrows():
            sid = srow["category_id"]
            quotes = select_quotes(tagged, sid, win_start, win_end, QUOTES_PER_SUBCATEGORY)
            top_drivers.append({
                "category_id": sid, "name": meta[sid]["name"],
                "recent_rate_pct": None if pd.isna(srow["recent_rate_pct"]) else round(srow["recent_rate_pct"], 3),
                "baseline_rate_pct": None if pd.isna(srow["baseline_rate_pct"]) else round(srow["baseline_rate_pct"], 3),
                "pp_delta": None if pd.isna(srow["pp_delta"]) else round(srow["pp_delta"], 3),
                "verdict": srow["verdict"],
                "quote": quotes[0] if quotes else None,
            })

        top_sub_name = top_drivers[0]["name"] if top_drivers and top_drivers[0]["pp_delta"] is not None else None
        top_sub_pp = top_drivers[0]["pp_delta"] if top_drivers and top_drivers[0]["pp_delta"] is not None else None

        # Prefer quotes representative of the top driving subcategory; fall
        # back to parent-level (any-subcategory-under-this-parent) quotes if
        # that subcategory doesn't have enough on its own.
        card_quotes = []
        if sub_rows.shape[0]:
            top_sid = sub_rows.iloc[0]["category_id"]
            card_quotes = select_quotes(tagged, top_sid, win_start, win_end, CARD_QUOTE_COUNT)
        if len(card_quotes) < CARD_QUOTE_COUNT:
            fallback = select_quotes(tagged, pid, win_start, win_end, CARD_QUOTE_COUNT)
            seen_ids = {q["review_id"] for q in card_quotes}
            for q in fallback:
                if q["review_id"] not in seen_ids and len(card_quotes) < CARD_QUOTE_COUNT:
                    card_quotes.append(q)

        recent_rate = prow["recent_rate_pct"] if pd.notna(prow["recent_rate_pct"]) else 0.0
        baseline_rate = prow["baseline_rate_pct"] if pd.notna(prow["baseline_rate_pct"]) else 0.0
        ratio = None if pd.isna(prow["ratio"]) else prow["ratio"]
        pp_delta_val = None if pd.isna(prow["pp_delta"]) else round(prow["pp_delta"], 3)
        recent_count_val = int(prow["recent_count"])

        cards.append({
            "category_id": pid,
            "category_name": meta[pid]["name"],
            "watch_category": is_watch,
            "watch_reason": meta[pid]["watch_reason"],
            "status": status,
            "title": card_title(meta[pid]["name"], status, ratio, recent_rate),
            "narrative": card_narrative(
                meta[pid]["name"], status, recent_rate, baseline_rate, ratio,
                recent_count_val, window_label, top_sub_name, top_sub_pp,
            ),
            "recent_rate_pct": round(recent_rate, 3), "baseline_rate_pct": round(baseline_rate, 3),
            "pp_delta": pp_delta_val,
            "ratio": None if ratio is None else round(ratio, 3),
            "recent_count": recent_count_val, "recent_total": int(prow["recent_total"]),
            "baseline_count": int(prow["baseline_count"]), "baseline_total": int(prow["baseline_total"]),
            "subcategory_contribution_sum_pct": round(sub_sum, 3),
            "multi_label_note": multi_label_note,
            "top_drivers": top_drivers,
            "quotes": card_quotes,
            "priority_score": round(priority_score(recent_count_val, pp_delta_val), 2),
        })

    cards_by_id = {c["category_id"]: c for c in cards}

    # Zone A: real confidence AND real movement -- ranked by priority_score,
    # restricted to categories clearing ZONE_A_MIN_VOLUME. Watch categories
    # are not exempt from this floor; they earn a Zone A slot on the same
    # merit as anything else (ai_coach's real volume/trend puts it here on
    # its own, independent of being a watch category).
    eligible = [c for c in cards if c["recent_count"] >= ZONE_A_MIN_VOLUME]
    zone_a_ids = [c["category_id"] for c in sorted(eligible, key=lambda c: c["priority_score"], reverse=True)][:ZONE_A_MAX_CARDS]

    # Zone B: both watch categories, always, regardless of volume or Zone A
    # membership -- if a watch category is also in Zone A that's expected,
    # not deduplicated away (the two zones answer different questions: "act
    # on this" vs. "we track this regardless").
    watch_zone_ids = watch_parent_ids

    return {
        "scope": scope,
        "window_label": window_label,
        "window_start": str(win_start.date()), "window_end": str((win_end - pd.Timedelta(days=1)).date()),
        "priority_score_formula": PRIORITY_SCORE_FORMULA,
        "zone_a_min_volume": ZONE_A_MIN_VOLUME,
        "zone_a_min_volume_reasoning": (
            f"{ZONE_A_MIN_VOLUME} recent mentions -- well above the {5}-mention floor used "
            f"elsewhere just to judge whether a rate is measurable at all; this feed is answering "
            f"'what should someone act on this week,' which needs real confidence in the number, "
            f"not just statistical measurability."
        ),
        "cards": cards_by_id,
        "zone_a_ids": zone_a_ids,
        "watch_zone_ids": watch_zone_ids,
    }


def main():
    print("Loading taxonomy + pipeline outputs (read-only, from backend/data/)...")
    taxonomy = load_taxonomy()
    meta = category_meta(taxonomy)
    all_category_ids = list(meta.keys())

    tagged = pd.read_csv(DATA_DIR / "tagged_reviews.csv")
    trends = pd.read_csv(DATA_DIR / "category_trends.csv")
    verdicts = pd.read_csv(DATA_DIR / "category_trend_verdicts.csv")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = build_snapshot(tagged, taxonomy, meta)
    (OUT_DIR / "snapshot.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote snapshot.json ({snapshot['total_reviews']} reviews, "
          f"{len(snapshot['parents'])} parent categories)")

    timeseries = build_trends_timeseries(trends, meta)
    (OUT_DIR / "trends_timeseries.json").write_text(json.dumps(timeseries, indent=2), encoding="utf-8")
    n_points = sum(len(v) for scope in timeseries.values() for v in scope.values())
    print(f"Wrote trends_timeseries.json ({n_points} data points across "
          f"{len(timeseries)} scopes)")

    verdict_records = build_trend_verdicts(verdicts, meta)
    (OUT_DIR / "trend_verdicts.json").write_text(json.dumps(verdict_records, indent=2), encoding="utf-8")
    print(f"Wrote trend_verdicts.json ({len(verdict_records)} scope x category verdicts)")

    print(f"Building review samples (cap {REVIEW_SAMPLE_CAP} most-recent per category)...")
    samples = build_review_samples(tagged, all_category_ids)
    (OUT_DIR / "review_samples.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8")
    total_sample_reviews = sum(len(v) for v in samples.values())
    print(f"Wrote review_samples.json ({total_sample_reviews} review entries across "
          f"{len(samples)} categories, capped at {REVIEW_SAMPLE_CAP}/category)")

    # category metadata (names, watch flags, parent/child structure) -- small, standalone,
    # so the frontend doesn't have to re-derive it from snapshot.json alone
    (OUT_DIR / "category_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote category_meta.json ({len(meta)} categories)")

    print("Building primary insight feed (parent-anchored cards, subcategory drivers, real quotes)...")
    tagged_dt = tagged.copy()
    tagged_dt["date_parsed"] = pd.to_datetime(tagged_dt["date"], format="mixed", utc=True).dt.tz_localize(None)
    insight_feed = build_insight_feed(tagged_dt, verdicts, trends, meta)
    (OUT_DIR / "insight_feed.json").write_text(json.dumps(insight_feed, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote insight_feed.json ({len(insight_feed['cards'])} total cards -- "
          f"Zone A: {len(insight_feed['zone_a_ids'])} {insight_feed['zone_a_ids']}, "
          f"Watch zone: {len(insight_feed['watch_zone_ids'])} {insight_feed['watch_zone_ids']}, "
          f"window {insight_feed['window_start']} to {insight_feed['window_end']})")

    print(f"\nAll exports written to {OUT_DIR}")


if __name__ == "__main__":
    main()
