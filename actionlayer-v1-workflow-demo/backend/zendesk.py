import os
import requests
from requests.auth import HTTPBasicAuth
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()


def fetch_tickets() -> list[dict]:
    subdomain = os.getenv("ZENDESK_SUBDOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    token = os.getenv("ZENDESK_API_TOKEN")

    url = f"https://{subdomain}.zendesk.com/api/v2/tickets.json?per_page=50&sort_by=created_at&sort_order=desc"
    auth = HTTPBasicAuth(f"{email}/token", token)

    try:
        response = requests.get(url, auth=auth, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Zendesk request failed: {str(e)}")

    raw_tickets = response.json().get("tickets", [])
    return [
        {
            "id": t.get("id"),
            "subject": t.get("subject", ""),
            "description": t.get("description", ""),
            "status": t.get("status", ""),
            "created_at": t.get("created_at", ""),
            "priority": t.get("priority", "normal"),
        }
        for t in raw_tickets
    ]
