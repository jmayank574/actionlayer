import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "tickets.json")


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
    tickets.append(ticket)
    _save_all(tickets)


def update_ticket_status(jira_id: str, status: str):
    tickets = load_tickets()
    for t in tickets:
        if t.get("jira_id") == jira_id:
            t["status"] = status
            break
    _save_all(tickets)


def get_all_tickets() -> list[dict]:
    tickets = load_tickets()
    return [t for t in tickets if t.get("status") != "draft"]
