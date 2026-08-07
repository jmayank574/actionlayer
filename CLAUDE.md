# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ActionLayer is a real-data customer-feedback pipeline for one product so far — **WHOOP** (category: Wearables & Fitness). It ingests real Google Play + App Store reviews, tags them against a bottom-up taxonomy via Claude, computes trend/velocity stats, and exports a static-JSON dashboard. No fabricated data anywhere in this path — every count, rate, and quote traces back to a real review.

An earlier prototype (Claude-knowledge-based insight generation, Jira/Slack integration) lives in `actionlayer-v1-workflow-demo/`, archived, not part of the current product, not referenced by anything below.

## Repository Structure

```
actionlayer/
├── backend/
│   ├── ingest.py                  # Pulls Google Play + App Store reviews, upserts into data/whoop_reviews_raw.csv
│   ├── ingestion/
│   │   ├── google_play.py         # google-play-scraper wrapper, paginates full history
│   │   ├── app_store.py           # Apple's public RSS feed (capped ~500 most-recent reviews)
│   │   ├── normalize.py           # Shapes both sources into one schema
│   │   └── merge.py               # Upsert logic: new reviews added, edits refreshed, aged-out
│   │                               #   App Store reviews carried forward instead of dropped
│   ├── tag_reviews.py             # Multi-label tags reviews via Claude; incremental by default
│   │                               #   (only new/FAILED review_ids call the API) -- --full forces
│   │                               #   a complete re-tag (needed after a taxonomy change)
│   ├── tagging/
│   │   ├── taxonomy_loader.py     # Reads data/taxonomy.yaml
│   │   ├── prompt.py              # Builds the tagging system prompt (cached) + batch user messages
│   │   ├── tagger.py              # Batched Claude calls, validates subcategory_ids, retries failures
│   │   └── code_mapping.py, few_shot.py
│   ├── analyze_trends.py          # Rate + velocity per category, per source scope (see below)
│   ├── export_dashboard_data.py   # Reshapes computed outputs into frontend/public/data/whoop/*.json
│   ├── sample_for_taxonomy.py, sample_eval_set.py, eval_tagger.py, revalidate_prompt_fix.py
│   │                               # Taxonomy-building and tagger-eval tooling (see docstrings)
│   └── data/
│       ├── whoop_reviews_raw.csv      # Ingested reviews (source of truth, upserted)
│       ├── taxonomy.yaml              # The taxonomy itself
│       ├── tagged_reviews.csv         # Per-review tags + confidence
│       ├── category_trends.csv, category_trend_verdicts.csv
│       ├── open_coding.csv, taxonomy_sample.csv, eval_sample.csv  # Taxonomy-building/eval samples
│       └── _archive/                  # Old prompt-tuning investigation, kept for reference
└── frontend/          # Vite + React + TypeScript dashboard (no live backend -- reads static JSON)
    ├── public/data/products.json         # Category → Product registry
    ├── public/data/whoop/*.json          # Exported pipeline output (only data source)
    └── src/
        ├── pages/CategoryLanding.tsx, CategoryPage.tsx, ProductDashboard.tsx
        ├── components/InsightFeed.tsx, InsightCard.tsx, WatchZone.tsx, TrendChart.tsx, ...
        └── lib/data.ts        # fetch + in-memory cache over the static JSON
```

## Dev Commands

**Pipeline (run in order; each is safe to re-run):**
```bash
cd backend
python ingest.py                 # upserts data/whoop_reviews_raw.csv
python tag_reviews.py            # incremental; --full to force a complete re-tag
python analyze_trends.py
python export_dashboard_data.py
```

**Dashboard:**
```bash
cd frontend
npm run dev        # localhost:5173
npm run build      # tsc -b && vite build
npx tsc -b         # type-check only
```

**Automation:** `.github/workflows/daily-pipeline.yml` runs the full pipeline daily (13:00 UTC) and commits changed outputs. Requires an `ANTHROPIC_API_KEY` repository secret — without it, the tagging step fails on any day with genuinely new reviews (harmless no-op on days with none).

## Architecture

### Data flow
```
ingest.py (Google Play + App Store)
  → data/whoop_reviews_raw.csv (upsert, keyed on source+review_id)
tag_reviews.py (Claude, incremental)
  → data/tagged_reviews.csv (multi-label: parent_category_tags, subcategory_tags, confidences)
analyze_trends.py
  → data/category_trends.csv (descriptive time series, adaptive monthly buckets)
  → data/category_trend_verdicts.csv (spike/decline verdicts vs. trailing baseline)
export_dashboard_data.py
  → frontend/public/data/whoop/{snapshot,trends_timeseries,trend_verdicts,review_samples,category_meta,insight_feed}.json
Vite dashboard reads the JSON directly (frontend/src/lib/data.ts) -- no backend server in this path.
```

### Ingestion upsert (backend/ingestion/merge.py)
Google Play's API returns full history every pull; Apple's public RSS feed only ever returns the ~500 most-recent reviews. A plain overwrite would silently lose any review older than that window on a repeat pull. `merge_upsert()` keys on `(source, review_id)`: new reviews are added, previously-seen reviews are refreshed if content changed (rating/date/text/app_version), and reviews this pull didn't return are carried forward untouched. `first_seen_at`/`last_seen_at` track provenance.

### Incremental tagging (backend/tag_reviews.py)
Tagging calls Claude and costs real money per review. Since the raw dataset only grows a handful of reviews per day, re-tagging the whole corpus on every run would be pure waste. Default behavior: only review_ids not already in `data/tagged_reviews.csv` (or previously `status=FAILED`) get sent to Claude; everything else is carried forward byte-for-byte. Quality stats (`other_ungrouped_rate`, `multi_label_rate` in `data/tag_run_stats.json`) are still computed over the *full* merged corpus each run, so drift is caught regardless of how much was freshly tagged. Use `--full` after a taxonomy change, when every review genuinely needs re-evaluation.

### Source-scope discipline (backend/analyze_trends.py)
Google Play has ~9 years of history; App Store only has what Apple's RSS window currently holds (recency-only). Every trend is computed **per source**, plus a `combined_overlap` scope restricted to the window where both sources have real coverage (Nov 2025 onward) — never mixing Google Play's full history with App Store's recency-only data, which would manufacture false spikes purely from source coverage. The dashboard's insight feed uses `combined_overlap` uniformly (one constant, `INSIGHT_FEED_SCOPE`, in `export_dashboard_data.py`) and every card discloses that scope (`SCOPE_LABEL` in `frontend/src/lib/trends.ts`) — an unlabeled rate is easy to misquote against the wrong source's history.

### Insight feed prioritization (backend/export_dashboard_data.py, `build_insight_feed`)
Two zones: **Zone A** ("Priority Insights") ranks categories by `priority_score = recent_count * abs(pp_delta)`, minimum 15 recent mentions, top 4–6 cards. **Watch Categories** always surfaces `ai_coach` and `health_signal_reliability` regardless of volume — stakes over frequency, defined via `watch_category`/`watch_reason` in `data/taxonomy.yaml`. Card titles and narratives are deterministic templates, never LLM-generated, to stay consistent with the no-fabrication discipline everywhere else in this pipeline.

## Environment Variables

**Backend** (`backend/.env`):
- `ANTHROPIC_API_KEY` — the only credential the current pipeline needs (tagging is the only step that calls a paid API)

**GitHub Actions:** `ANTHROPIC_API_KEY` as a repository secret, for the same reason.

## Key Constraints

- **No fabricated data**: every review, count, and quote in the dashboard traces back to a live Google Play or App Store response. Card titles/narratives are deterministic templates, not model-generated.
- **Never mix source scopes**: Google Play's full history and App Store's RSS-window-only data must never be blended outside the explicit `combined_overlap` window (Nov 2025+). Every dashboard number must disclose which scope it's from.
- **Ingestion is append-only in spirit**: `ingest.py` upserts, never overwrites. A review must never disappear from `whoop_reviews_raw.csv` just because a later pull didn't happen to return it.
- **Tagging is incremental by default**: don't re-tag the whole corpus casually — it costs real money. Use `--full` only when the taxonomy itself has changed.
- **`backend/data/*.csv` and `frontend/public/data/whoop/*.json` are committed to git** — this is the persistence layer; there's no database and no long-running server.
