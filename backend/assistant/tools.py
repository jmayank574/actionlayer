"""Real-data tools the Assistant agent can call. Every tool reads directly
from the already-computed pipeline outputs (backend/data/*.csv,
data/taxonomy.yaml) -- nothing here invents data. A tool either returns real
rows straight from those files or an empty result; there is no path from a
tool call to a fabricated number or quote.

Loaded once at server startup (AssistantData()) and reused across requests --
these files are only a few MB and change at most once a day.
"""

from pathlib import Path

import pandas as pd

from tagging.taxonomy_loader import load_taxonomy

DATA_DIR = Path(__file__).parent.parent / "data"

DEFAULT_SCOPE = "combined_overlap"
MAX_SEARCH_LIMIT = 25


def _has_tag(tags_field: str, category_id: str) -> bool:
    return category_id in (tags_field or "").split(";")


class AssistantData:
    def __init__(self):
        self.tagged = pd.read_csv(DATA_DIR / "tagged_reviews.csv")
        self.tagged["parent_category_tags"] = self.tagged["parent_category_tags"].fillna("")
        self.tagged["subcategory_tags"] = self.tagged["subcategory_tags"].fillna("")
        self.tagged["text"] = self.tagged["text"].fillna("")

        self.trends = pd.read_csv(DATA_DIR / "category_trends.csv")
        self.verdicts = pd.read_csv(DATA_DIR / "category_trend_verdicts.csv")

        self.taxonomy = load_taxonomy()
        self.category_names: dict[str, str] = {}
        for cat in self.taxonomy["categories"]:
            self.category_names[cat["id"]] = cat["name"]
            for sub in cat["subcategories"]:
                self.category_names[sub["id"]] = sub["name"]

    def list_categories(self) -> list[dict]:
        out = []
        for cat in self.taxonomy["categories"]:
            out.append({
                "id": cat["id"], "name": cat["name"], "level": "parent",
                "watch_category": bool(cat.get("watch_category")),
            })
            for sub in cat["subcategories"]:
                out.append({
                    "id": sub["id"], "name": sub["name"], "level": "subcategory",
                    "parent_id": cat["id"],
                })
        return out

    def search_reviews(self, query: str | None = None, category_id: str | None = None,
                        source: str | None = None, min_rating: int | None = None,
                        max_rating: int | None = None, limit: int = 10) -> list[dict]:
        df = self.tagged
        if category_id:
            mask = df["parent_category_tags"].apply(lambda s: _has_tag(s, category_id)) | \
                   df["subcategory_tags"].apply(lambda s: _has_tag(s, category_id))
            df = df[mask]
        if source:
            df = df[df["source"] == source]
        if min_rating is not None:
            df = df[df["rating"] >= min_rating]
        if max_rating is not None:
            df = df[df["rating"] <= max_rating]
        if query:
            terms = [t.strip().lower() for t in query.split() if t.strip()]
            if terms:
                text_lower = df["text"].str.lower()
                mask = pd.Series(True, index=df.index)
                for t in terms:
                    mask &= text_lower.str.contains(t, regex=False, na=False)
                df = df[mask]

        df = df.sort_values("date", ascending=False).head(min(limit, MAX_SEARCH_LIMIT))
        results = []
        for _, r in df.iterrows():
            results.append({
                "review_id": r["review_id"],
                "source": r["source"],
                "rating": int(r["rating"]) if pd.notna(r["rating"]) else None,
                "date": r["date"],
                "text": r["text"][:600],
                "categories": [c for c in r["subcategory_tags"].split(";") if c],
            })
        return results

    def category_stats(self, category_id: str | None = None, scope: str = DEFAULT_SCOPE) -> list[dict]:
        df = self.verdicts[self.verdicts["scope"] == scope]
        if category_id:
            df = df[df["category_id"] == category_id]
        out = []
        for _, r in df.iterrows():
            out.append({
                "category_id": r["category_id"],
                "category_name": self.category_names.get(r["category_id"], r["category_id"]),
                "level": r["level"], "scope": r["scope"],
                "recent_rate_pct": r["recent_rate_pct"], "baseline_rate_pct": r["baseline_rate_pct"],
                "pp_delta": r["pp_delta"], "ratio": r["ratio"],
                "recent_count": int(r["recent_count"]), "baseline_count": int(r["baseline_count"]),
                "verdict": r["verdict"], "flagged_spike": bool(r["flagged_spike"]),
                "flagged_decline": bool(r["flagged_decline"]),
            })
        return out

    def trend_timeseries(self, category_id: str, scope: str = DEFAULT_SCOPE) -> list[dict]:
        df = self.trends[(self.trends["category_id"] == category_id) & (self.trends["scope"] == scope)]
        df = df.sort_values("period_start")
        out = []
        for _, r in df.iterrows():
            out.append({
                "period": r["period"], "period_type": r["period_type"],
                "period_start": r["period_start"], "period_end": r["period_end"],
                "rate_pct": r["rate_pct"], "tag_count": int(r["tag_count"]),
                "total_reviews": int(r["total_reviews"]),
                "adequate_volume": bool(r["adequate_volume"]),
                "in_recent_window": bool(r["in_recent_window"]),
                "flagged_spike": bool(r["flagged_spike"]), "flagged_decline": bool(r["flagged_decline"]),
            })
        return out
