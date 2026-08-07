import base64
import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv
from models import GeneratedTicket

load_dotenv()


def push_ticket(ticket: GeneratedTicket, cluster_title: str) -> dict:
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY")

    credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    criteria_items = [
        {
            "type": "listItem",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": criterion}],
                }
            ],
        }
        for criterion in ticket.acceptanceCriteria
    ]

    body = {
        "fields": {
            "project": {"key": project_key},
            "summary": ticket.title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": ticket.description}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Acceptance Criteria:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": criteria_items,
                    },
                ],
            },
            "issuetype": {"name": "Story"},
            "labels": ticket.labels,
        }
    }

    try:
        response = requests.post(
            f"{base_url}/rest/api/3/issue",
            json=body,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        error_msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_msg = e.response.json()
            except Exception:
                error_msg = e.response.text
        raise HTTPException(status_code=502, detail=f"Jira request failed: {error_msg}")

    data = response.json()
    jira_id = data.get("id")
    jira_key = data.get("key")
    jira_url = f"{base_url}/browse/{jira_key}"

    return {"jira_id": jira_id, "jira_key": jira_key, "jira_url": jira_url, "success": True}
