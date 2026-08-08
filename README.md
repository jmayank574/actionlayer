# ActionLayer

A real-data customer-feedback intelligence pipeline. Right now it covers one product — **WHOOP** (Wearables & Fitness) — end to end: real reviews in, a prioritized insight dashboard out. No fabricated data, no LLM-invented statistics — every number on the dashboard traces back to an actual Google Play or App Store review.

## How it works

```
Google Play + App Store  →  ingest.py  →  data/whoop_reviews_raw.csv
                                              (upsert — reviews never disappear
                                               when Apple's ~500-review RSS
                                               window rolls forward)
                                                  ↓
                          tag_reviews.py (Claude, incremental —
                          only new/failed reviews call the API)
                                                  ↓
                          data/tagged_reviews.csv (bottom-up taxonomy,
                          multi-label, taxonomy.yaml)
                                                  ↓
                          analyze_trends.py → category_trends.csv,
                          category_trend_verdicts.csv (rate + velocity
                          per category, per source scope)
                                                  ↓
                          export_dashboard_data.py → frontend/public/data/whoop/*.json
                                                  ↓
                          Vite + React dashboard (Insights feed +
                          Explore-all-categories view)
```

A GitHub Actions workflow (`.github/workflows/daily-pipeline.yml`) runs this whole chain daily — new reviews get ingested, tagged, and reflected in the dashboard automatically.

## Setup

**`backend/.env`**
```
ANTHROPIC_API_KEY=
```

That's the only credential the current pipeline needs — tagging is the only step that calls an external paid API.

## Run locally

```bash
# Ingest, tag, and analyze (run once, or after adding new data)
cd backend
pip install -r requirements.txt
python ingest.py                # pull new reviews (upsert, safe to re-run)
python tag_reviews.py           # tag only new/failed reviews via Claude
python analyze_trends.py        # recompute trend/velocity stats
python export_dashboard_data.py # export dashboard JSON

# Dashboard
cd frontend
npm install
npm run dev        # localhost:5173
```

## Assistant

A chat interface for asking free-form questions about the review data — modeled on Unwrap's Assistant. Claude gets real tools (search reviews, pull category stats, get a trend time series) and reasons across multiple calls before answering; every quote and number in its response has to come from a tool call, never from memory. This is the one live-backend piece of the app:

```bash
# alongside the dashboard's npm run dev
cd backend
uvicorn assistant_server:app --reload --port 8001
```

Then open the Assistant page from the dashboard sidebar. Local dev only for now — nothing deployed yet.

## Stack

- **AI:** Anthropic Claude (`claude-sonnet-4-6`) — review tagging, and the Assistant's tool-calling chat
- **Pipeline:** Python, pandas
- **Dashboard:** Vite, React, TypeScript, Tailwind CSS v4, recharts — mostly a static site reading pre-computed JSON, plus the live Assistant backend (FastAPI) described above
- **Automation:** GitHub Actions (daily ingest → tag → trend → export → commit)

## Archive

`actionlayer-v1-workflow-demo/` holds an earlier prototype (Claude-knowledge-based insight generation, Jira ticket creation, Slack notifications). It's set aside, not deleted, and isn't part of the current product.
