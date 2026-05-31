# ActionLayer

ActionLayer turns public customer feedback into shipped engineering fixes — automatically. Enter any company and product, and Claude analyzes public review knowledge to surface the top 5 critical issues, generate Jira-ready tickets, track them through resolution, and notify your CS team via Slack when the loop closes.

**Live demo:** https://frontend-one-rose-77.vercel.app

## How it works

1. Enter a product (e.g. Slack · Huddle) — Claude synthesizes public G2, Reddit, and App Store feedback into 5 prioritized insight clusters
2. Click **Generate Ticket** — Claude writes a complete Jira ticket with acceptance criteria, story points, and priority
3. Click **Push to Jira** — ticket is created live in your Jira project
4. **Loop Tracker** syncs Jira status in real time and shows time-to-resolution for every issue
5. Click **Send to Slack** — CS team gets notified when a fix ships

## Setup

**`backend/.env`**
```
ANTHROPIC_API_KEY=
JIRA_BASE_URL=           # e.g. https://yourorg.atlassian.net
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=        # e.g. SCRUM
SLACK_WEBHOOK_URL=       # optional — for CS notifications
```

**`frontend/.env.local`**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Stack

- **AI:** Anthropic Claude (`claude-sonnet-4-6`)
- **Backend:** Python, FastAPI — hosted on Railway
- **Frontend:** Next.js 16, TypeScript, Tailwind CSS — hosted on Vercel
- **Integrations:** Jira REST API v3, Slack Incoming Webhooks
