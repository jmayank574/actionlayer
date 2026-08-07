import json
import os
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "tickets.json")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def init_storage():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump([], f)


def load_tickets() -> list[dict]:
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def _save_all(tickets: list[dict]):
    with open(DATA_PATH, "w") as f:
        json.dump(tickets, f, indent=2)


def save_ticket(ticket: dict):
    tickets = load_tickets()
    now = _now_iso()
    ticket["pushed_at"] = now
    ticket.setdefault("created_at", now)
    ticket["resolved_at"] = None
    ticket["shipped_at"] = None
    ticket["days_to_resolve"] = None
    ticket["status_history"] = [{"status": "open", "timestamp": now}]
    tickets.append(ticket)
    _save_all(tickets)


def update_ticket_status(jira_id: str, new_status: str):
    tickets = load_tickets()
    now = _now_iso()
    for t in tickets:
        if t.get("jira_id") != jira_id:
            continue
        t["status"] = new_status
        if "status_history" not in t:
            t["status_history"] = []
        t["status_history"].append({"status": new_status, "timestamp": now})
        if new_status.lower() in ("done", "closed", "resolved"):
            t["resolved_at"] = now
            t["shipped_at"] = now
            ref = t.get("pushed_at") or t.get("created_at")
            if ref:
                try:
                    diff = (_parse_iso(now) - _parse_iso(ref)).total_seconds() / 86400
                    t["days_to_resolve"] = round(diff, 1)
                except Exception:
                    pass
        break
    _save_all(tickets)


def get_all_tickets() -> list[dict]:
    tickets = load_tickets()
    return sorted(
        [t for t in tickets if t.get("status") != "draft"],
        key=lambda t: t.get("created_at", ""),
        reverse=True,
    )


def get_ticket_history() -> list[dict]:
    return get_all_tickets()
