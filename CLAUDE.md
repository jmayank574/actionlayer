# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

```
actionlayer/
├── backend/          # Python FastAPI server
│   ├── main.py       # All routes + startup cache logic
│   ├── claude_service.py  # All Claude API calls
│   ├── jira_service.py    # Jira REST API integration
│   ├── storage.py         # JSON file persistence for tickets
│   ├── models.py          # Pydantic request/response models
│   ├── scraper.py         # (unused) original two-call scraper
│   └── data/
│       ├── tickets.json           # Persisted ticket history
│       └── public_cache/          # Disk-backed cluster cache (runtime-generated)
└── frontend/         # Next.js 14 App Router
    ├── app/page.tsx          # Main dashboard
    ├── app/tracker/page.tsx  # Loop Tracker
    └── .env.local            # NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Dev Commands

**Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev        # localhost:3000
npm run build      # production build
npx tsc --noEmit   # type-check only
```

**Deploy:**
```bash
# Backend auto-deploys to Railway on git push to main
git push origin main

# Frontend must be manually deployed (not connected to GitHub auto-deploy)
cd frontend && npx vercel --prod
```

## Architecture

### Data Flow
```
User enters company + product
  → GET /api/insights?company=X&product=Y
  → _compute_insights() checks: memory cache → disk cache → Claude API
  → claude_service.generate_clusters_from_public() — single Claude call
  → Returns 5 InsightCluster objects with source="public"
  → Clusters saved to data/public_cache/<key>.json (7-day TTL)

User clicks "Generate Ticket"
  → POST /api/generate-ticket {cluster}
  → claude_service.generate_ticket() → GeneratedTicket

User clicks "Push to Jira"
  → POST /api/push-to-jira {ticket, cluster_id, cluster_title}
  → jira_service.push_ticket() creates Story via Jira REST API v3 (ADF format)
  → storage.save_ticket() appends to data/tickets.json with full status_history

Loop Tracker (GET /api/tracker)
  → Fetches live Jira status for each ticket
  → Calls storage.update_ticket_status() on changes (tracks resolved_at, days_to_resolve)

Slack notification
  → POST /api/notify-slack → Slack Incoming Webhook
```

### Three-Tier Cache (backend/main.py)
1. **Memory** (`_insights_cache` dict, 10-min TTL) — fastest, reset on process restart
2. **Disk** (`data/public_cache/*.json`, 7-day TTL) — survives Railway process restarts
3. **Claude API** — called only on cache miss, takes ~15–20 seconds

On startup, `prewarm_cache()` loads disk files into memory, then sequentially generates any missing quick-picks (Unwrap, Slack, GitHub, Notion, Jira) in the background.

### Claude API Usage (backend/claude_service.py)
All three functions use `claude-sonnet-4-6`, max_tokens 1500–3000. Claude sometimes returns markdown-fenced JSON despite instructions — `_strip_fences()` handles this. Snake_case field normalization is done in the frontend `handleGenerateTicket` function, not the backend.

### Frontend State (frontend/app/page.tsx)
- Clusters cached in `localStorage` under key `actionlayer_insights_v2` as `{company, product, clusters}`
- On mount: restores from localStorage OR auto-loads Slack/Huddle if no cache
- `lastAnalyzed` state drives the active pill highlight and subtitle text
- `loadingFor` state drives the loading banner message

### Storage (backend/storage.py)
`data/tickets.json` is a flat JSON array. Every ticket has `status_history` (array of `{status, timestamp}`), `pushed_at`, `resolved_at`, `shipped_at`, and `days_to_resolve`. **This file is committed to git** — Railway's filesystem is ephemeral on redeploy, so ticket history must live in git.

## Environment Variables

**Backend** (`backend/.env`):
- `ANTHROPIC_API_KEY`
- `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_PROJECT_KEY`
- `SLACK_WEBHOOK_URL`

**Frontend** (`frontend/.env.local`):
- `NEXT_PUBLIC_API_URL` — points to backend (`http://localhost:8000` locally, Railway URL in production)

## Key Constraints

- **Railway ephemeral storage**: Files written at runtime survive process restarts but are wiped on redeploy. `tickets.json` must be committed to git to persist across deploys. `public_cache/` is intentionally ephemeral.
- **Jira description format**: Must use Atlassian Document Format (ADF), not plain text or markdown. See `jira_service.py` for the exact structure.
- **Claude JSON parsing**: Always use `_strip_fences()` before `json.loads()` on Claude responses. Claude ignores "no markdown" instructions intermittently.
- **CORS**: Set to `allow_origins=["*"]` intentionally for demo — Vercel frontend calls Railway backend cross-origin.
