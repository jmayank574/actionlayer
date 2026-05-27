import os
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import base64

import storage
import zendesk
import claude_service
import jira_service
from models import GenerateRequest, PushToJiraRequest

load_dotenv()

storage.init_storage()

app = FastAPI(title="ActionLayer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://frontend-one-rose-77.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


CLUSTERS_CACHE = Path("data/clusters_cache.json")

@app.get("/api/insights")
def get_insights():
    if CLUSTERS_CACHE.exists():
        return json.loads(CLUSTERS_CACHE.read_text())
    raise HTTPException(status_code=503, detail="No cached insights available. Use Import from Unwrap to load feedback.")


@app.post("/api/generate-ticket")
def api_generate_ticket(request: GenerateRequest):
    ticket = claude_service.generate_ticket(request.cluster)
    return ticket


@app.post("/api/generate-prd")
def api_generate_prd(request: GenerateRequest):
    prd = claude_service.generate_prd(request.cluster)
    return prd


@app.post("/api/push-to-jira")
def api_push_to_jira(request: PushToJiraRequest):
    result = jira_service.push_ticket(request.ticket, request.cluster_title)
    storage.save_ticket(
        {
            "jira_id": result["jira_id"],
            "jira_key": result["jira_key"],
            "jira_url": result["jira_url"],
            "cluster_id": request.cluster_id,
            "cluster_title": request.cluster_title,
            "title": request.ticket.title,
            "priority": request.ticket.priority,
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {"success": True, "jira_key": result["jira_key"], "jira_url": result["jira_url"]}


@app.get("/api/tracker")
def api_tracker():
    tickets = storage.get_all_tickets()
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Accept": "application/json",
    }

    for ticket in tickets:
        jira_id = ticket.get("jira_id")
        if not jira_id:
            continue
        try:
            resp = requests.get(
                f"{base_url}/rest/api/3/issue/{jira_id}",
                headers=headers,
                timeout=10,
            )
            if resp.ok:
                live_status = resp.json().get("fields", {}).get("status", {}).get("name", "")
                if live_status and live_status != ticket.get("status"):
                    storage.update_ticket_status(jira_id, live_status)
                    ticket["status"] = live_status
        except Exception:
            pass

    return tickets


@app.post("/api/ingest-csv")
def ingest_csv(body: dict):
    text = body.get("text", "")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="No feedback lines provided")

    tickets = []

    # Reconstruct Zendesk tickets from cached clusters so both sources cluster together
    if CLUSTERS_CACHE.exists():
        cached_clusters = json.loads(CLUSTERS_CACHE.read_text())
        for cluster in cached_clusters:
            for verbatim in cluster.get("verbatims", []):
                tickets.append({
                    "id": f"zendesk-{len(tickets)}",
                    "subject": verbatim,
                    "description": verbatim,
                    "status": "open",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "priority": "normal",
                    "source": "zendesk",
                })

    # Add Unwrap feedback lines
    for i, line in enumerate(lines):
        tickets.append({
            "id": f"unwrap-{i}",
            "subject": line,
            "description": line,
            "status": "open",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "priority": "normal",
            "source": "unwrap",
        })

    clusters = claude_service.cluster_feedback(tickets)
    for c in clusters:
        c.source = "zendesk+unwrap"
    return clusters
