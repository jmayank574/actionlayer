import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import base64

import storage
import claude_service
import jira_service
from models import GenerateRequest, PushToJiraRequest

load_dotenv()

storage.init_storage()

app = FastAPI(title="ActionLayer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


RESOLVED = {"done", "closed", "resolved"}
_insights_cache: dict[str, tuple[float, list]] = {}
CACHE_TTL = 600  # 10 minutes in memory
DISK_CACHE_DIR = Path("data/public_cache")
DISK_CACHE_TTL = 86400 * 7  # 7 days on disk

QUICK_PICKS = [
    ("Unwrap", "Customer Intelligence"),
    ("Slack", "Huddle"),
    ("GitHub", "Copilot"),
    ("Notion", "AI"),
    ("Jira", "Cloud"),
]


def _disk_path(cache_key: str) -> Path:
    return DISK_CACHE_DIR / f"{cache_key.replace(':', '__')}.json"


def _load_disk(cache_key: str) -> list | None:
    path = _disk_path(cache_key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data.get("saved_at", 0) > DISK_CACHE_TTL:
            return None
        return data["clusters"]
    except Exception:
        return None


def _save_disk(cache_key: str, clusters: list):
    DISK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _disk_path(cache_key).write_text(json.dumps({"saved_at": time.time(), "clusters": clusters}))


def _compute_insights(company: str, product: str) -> list:
    cache_key = f"{company.strip().lower()}:{product.strip().lower()}"
    now = time.time()

    # 1. Memory cache
    if cache_key in _insights_cache:
        cached_at, cached_data = _insights_cache[cache_key]
        if now - cached_at < CACHE_TTL:
            return cached_data

    # 2. Disk cache (survives process restarts)
    disk_data = _load_disk(cache_key)
    if disk_data is not None:
        _insights_cache[cache_key] = (now, disk_data)
        return disk_data

    # 3. Generate fresh via Claude
    clusters = claude_service.generate_clusters_from_public(company, product)
    for c in clusters:
        c.source = "public"

    ticket_map: dict[str, dict] = {}
    for t in storage.get_all_tickets():
        cid = t.get("cluster_id")
        if not cid:
            continue
        if cid not in ticket_map or t.get("created_at", "") > ticket_map[cid].get("created_at", ""):
            ticket_map[cid] = t

    result = []
    for cluster in clusters:
        cid = cluster.id
        ticket = ticket_map.get(cid)
        if ticket and ticket.get("status", "").lower() in RESOLVED:
            continue
        cluster_dict = cluster.model_dump()
        cluster_dict["ticket"] = {
            "jira_key": ticket["jira_key"],
            "jira_url": ticket["jira_url"],
            "status": ticket["status"],
        } if ticket else None
        result.append(cluster_dict)

    _insights_cache[cache_key] = (now, result)
    _save_disk(cache_key, result)
    return result


@app.on_event("startup")
async def prewarm_cache():
    # Load existing disk cache into memory first — instant, no Claude calls
    if DISK_CACHE_DIR.exists():
        for f in DISK_CACHE_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                if time.time() - data.get("saved_at", 0) < DISK_CACHE_TTL:
                    cache_key = f.stem.replace("__", ":")
                    _insights_cache[cache_key] = (data["saved_at"], data["clusters"])
                    print(f"[startup] Loaded from disk: {cache_key}")
            except Exception:
                pass

    # Pre-warm any quick-picks not yet on disk — sequentially to avoid overloading
    async def prewarm_missing():
        for company, product in QUICK_PICKS:
            cache_key = f"{company.lower()}:{product.lower()}"
            if cache_key in _insights_cache:
                continue
            try:
                print(f"[prewarm] Generating {company} / {product}")
                await asyncio.to_thread(_compute_insights, company, product)
                print(f"[prewarm] Done {company} / {product}")
            except Exception as e:
                print(f"[prewarm] Failed {company} / {product}: {e}")

    asyncio.create_task(prewarm_missing())


@app.get("/api/insights")
def get_insights(
    company: str = Query(default="Slack"),
    product: str = Query(default="Huddle"),
    refresh: bool = Query(default=False),
):
    cache_key = f"{company.strip().lower()}:{product.strip().lower()}"
    if refresh and cache_key in _insights_cache:
        del _insights_cache[cache_key]
    return _compute_insights(company, product)


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


@app.post("/api/notify-slack")
def notify_slack(body: dict):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return {"success": False, "not_configured": True}

    ticket_title = body.get("ticket_title", "")
    cluster_title = body.get("cluster_title", "")
    jira_key = body.get("jira_key", "")
    jira_url = body.get("jira_url", "")

    payload = {
        "text": "✅ Fix shipped",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Fix shipped:* {ticket_title}\n*Customer issue resolved:* {cluster_title}\n*Jira:* <{jira_url}|{jira_key}>\nCS team: customers reporting this issue should see it resolved.",
                },
            }
        ],
    }

    resp = requests.post(webhook_url, json=payload, timeout=10)
    if resp.ok:
        return {"success": True}
    raise HTTPException(status_code=500, detail=f"Slack webhook failed: {resp.text}")


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


