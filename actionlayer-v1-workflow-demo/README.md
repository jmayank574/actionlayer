# ActionLayer v1 — workflow automation demo

This is the original ActionLayer build. It's archived here, not deleted, because the
project's center of gravity moved to a different data foundation — see below — but the
mechanics in this code are real and still work.

## What this demonstrates

An end-to-end agentic workflow: **feedback signal → routed engineering ticket → generated
doc → tracked to resolution → team notified.**

1. Enter a company + product — Claude synthesizes what it knows about public feedback
   (G2, Reddit, App Store) into 5 prioritized insight clusters
2. Generate a Jira-ready ticket from a cluster — acceptance criteria, priority, story points
3. Push it live to a real Jira project (Jira REST API v3, Atlassian Document Format)
4. Loop Tracker polls Jira and shows real time-to-resolution
5. Notify a CS team in Slack when a fix ships (Incoming Webhook)

## Why it's separated, not deleted

The current project (`backend/` at the repo root) is built on a real data foundation: reviews
actually scraped from Google Play and the App Store, an evidence-based taxonomy built from
reading real reviews, a validated multi-label tagger scored against a held-out human-labeled
set, and trend/velocity analysis on top of that. This code predates all of that — the insight
step here is Claude drawing on its own training knowledge of a product's public reputation,
not real ingested data. That's a fundamentally different data source, not a smaller version of
the same thing, so it doesn't belong mixed into the same working directory as the real
pipeline going forward.

**This is not dead weight.** The Jira integration, the Slack notification, and the
ticket/PRD-generation prompts are real, working, independent of where the input cluster came
from. If the current project ever needs "turn a validated trend into a routed ticket," this is
where that code already exists — it would need to be pointed at the new data model
(`Category → Product → Dashboard`, see the repo root) instead of the old ad-hoc
`InsightCluster` schema, but the Jira/Slack mechanics themselves don't need to be rebuilt.

## Structure

```
actionlayer-v1-workflow-demo/
├── backend/
│   ├── main.py            # FastAPI server — all v1 routes
│   ├── claude_service.py  # Claude-knowledge-based insight/ticket/PRD generation
│   ├── jira_service.py    # Jira REST API v3 integration
│   ├── models.py          # v1 schema (InsightCluster, GeneratedTicket, GeneratedPRD)
│   ├── storage.py         # JSON ticket persistence
│   ├── scraper.py         # unused even in v1 — an early two-call scraper, superseded
│   ├── zendesk.py         # unused — leftover from a pre-v1 iteration, never wired to any route
│   ├── Procfile            # Railway deploy config (`uvicorn main:app`)
│   └── data/
│       ├── tickets.json         # v1 ticket history
│       ├── clusters_cache.json  # v1 insight cluster cache
│       └── public_cache/        # v1 disk-backed cluster cache (was runtime-generated)
└── frontend/                # Next.js dashboard — 100% built against the v1 API above
```

## Running this demo (unchanged from before the move)

```bash
cd actionlayer-v1-workflow-demo/backend
pip install -r ../../backend/requirements.txt   # requirements.txt stayed at the repo root; fastapi/uvicorn/anthropic cover this
uvicorn main:app --reload --port 8000

# separate terminal
cd actionlayer-v1-workflow-demo/frontend
npm install
npm run dev
```

Needs the same `.env` values as before (`ANTHROPIC_API_KEY`, `JIRA_BASE_URL`, `JIRA_EMAIL`,
`JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`, `SLACK_WEBHOOK_URL`) and
`frontend/.env.local` (`NEXT_PUBLIC_API_URL=http://localhost:8000`).

`scraper.py` and `zendesk.py` are included for completeness but were never wired into any
route even in v1 — confirmed via grep before this move, kept only so the archive is a
complete, honest snapshot of what existed at the time, not a curated subset.
