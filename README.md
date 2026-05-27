# ActionLayer

ActionLayer pulls raw support tickets from Zendesk, uses Claude AI to cluster them into insight themes, and lets you generate structured Jira tickets and one-page PRDs with a single click — closing the loop between customer feedback and engineering.

## Setup

Fill in `backend/.env` with your credentials:

```
ANTHROPIC_API_KEY=
ZENDESK_SUBDOMAIN=       # e.g. mycompany (no .zendesk.com)
ZENDESK_EMAIL=           # your Zendesk login email
ZENDESK_API_TOKEN=       # Zendesk API token (not password)
JIRA_BASE_URL=           # e.g. https://mycompany.atlassian.net
JIRA_EMAIL=              # your Jira login email
JIRA_API_TOKEN=          # Jira API token
JIRA_PROJECT_KEY=        # e.g. ENG
```

## Run the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

## Open the app

- Dashboard: http://localhost:3000
- Loop Tracker: http://localhost:3000/tracker
- API docs: http://localhost:8000/docs

## CSV / Unwrap import

Use `POST /api/ingest-csv` with `{ "text": "one feedback item per line" }` to cluster feedback from any tool including Unwrap.ai exports.
