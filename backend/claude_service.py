import json
import os
import re
import anthropic
from fastapi import HTTPException
from dotenv import load_dotenv
from models import InsightCluster, GeneratedTicket, GeneratedPRD

load_dotenv()

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def _strip_fences(text: str) -> str:
    """Remove markdown code fences Claude sometimes adds despite being told not to."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_clusters_from_public(company_name: str, product_name: str) -> list[InsightCluster]:
    """Single-call approach: Claude acts as a product analyst who has synthesized public reviews."""
    client = _get_client()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=(
            "You are a senior product analyst who has deeply researched customer feedback "
            "across G2, Reddit, App Store, Twitter, and Capterra. You surface the most important, "
            "actionable insight clusters that engineering teams should address. "
            "Return a JSON array only — no markdown, no explanation. Each object must have:\n"
            "- id: short unique slug (e.g. 'audio-drops')\n"
            "- title: concise cluster name, 3-7 words\n"
            "- severity: 'high', 'medium', or 'low' based on user impact and frequency\n"
            "- frequency: estimated number of affected users reporting this (integer)\n"
            "- summary: exactly 2 sentences — what breaks and why it matters to users\n"
            "- verbatims: array of exactly 3 realistic user quotes — specific, first-person, "
            "mentioning actual features or workflows, sounding like real reviews\n\n"
            "Focus on themes that are: actionable by engineering, grounded in the product's actual "
            "feature set, and varied (mix of bugs, missing features, UX friction, performance)."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Based on your comprehensive knowledge of public user feedback for "
                f"{product_name} by {company_name}, identify the 5 most important recurring "
                f"pain points users report across review platforms. Surface what real customers "
                f"actually say — be specific to {product_name}'s actual features and workflows."
            ),
        }],
    )

    raw = _strip_fences(message.content[0].text)
    try:
        clusters_data = json.loads(raw)
        return [InsightCluster(**c) for c in clusters_data]
    except (json.JSONDecodeError, Exception) as e:
        print(f"[generate_clusters_from_public] Raw response: {raw}")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


def cluster_feedback(tickets: list[dict]) -> list[InsightCluster]:
    client = _get_client()
    tickets_text = json.dumps(tickets, indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=(
            "You are a product analytics engine. Given raw customer support tickets, "
            "identify the most important recurring themes. Group them into 4-6 insight clusters. "
            "Return a JSON array only — no markdown, no explanation. Each object must have:\n"
            "- id: a short unique slug like 'checkout-failures'\n"
            "- title: short descriptive name of the problem\n"
            "- severity: 'high', 'medium', or 'low' based on user impact\n"
            "- frequency: estimated number of tickets in this cluster\n"
            "- summary: exactly 2 sentences describing the problem\n"
            "- verbatims: array of exactly 3 real quotes copied from the tickets"
        ),
        messages=[{"role": "user", "content": f"Here are the support tickets:\n\n{tickets_text}"}],
    )

    raw = _strip_fences(message.content[0].text)
    try:
        clusters_data = json.loads(raw)
        return [InsightCluster(**c) for c in clusters_data]
    except (json.JSONDecodeError, Exception) as e:
        print(f"[cluster_feedback] Raw response: {raw}")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


def generate_ticket(cluster: InsightCluster) -> GeneratedTicket:
    client = _get_client()
    cluster_text = json.dumps(cluster.model_dump(), indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=(
            "You are a senior product manager. Given a customer feedback cluster, "
            "write a Jira-ready engineering ticket. Return JSON only — no markdown, no explanation. Fields:\n"
            "- title: concise action-oriented title under 60 characters\n"
            "- description: 2-3 sentences explaining the problem and user impact\n"
            "- acceptanceCriteria: array of exactly 4 criteria in Given/When/Then format\n"
            "- priority: 'P1', 'P2', or 'P3' based on severity\n"
            "- storyPoints: integer from 1 to 8\n"
            "- labels: array of 2-4 relevant engineering tags\n"
            "- customerQuotes: the 2 most impactful verbatim quotes from the cluster"
        ),
        messages=[{"role": "user", "content": f"Here is the feedback cluster:\n\n{cluster_text}"}],
    )

    raw = _strip_fences(message.content[0].text)
    try:
        ticket_data = json.loads(raw)
        # normalize snake_case keys Claude sometimes returns
        ticket_data["acceptanceCriteria"] = ticket_data.pop("acceptanceCriteria", None) or ticket_data.pop("acceptance_criteria", [])
        ticket_data["storyPoints"] = ticket_data.pop("storyPoints", None) or ticket_data.pop("story_points", 3)
        ticket_data["customerQuotes"] = ticket_data.pop("customerQuotes", None) or ticket_data.pop("customer_quotes", [])
        return GeneratedTicket(**ticket_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[generate_ticket] Raw response: {raw}")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")


def generate_prd(cluster: InsightCluster) -> GeneratedPRD:
    client = _get_client()
    cluster_text = json.dumps(cluster.model_dump(), indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=(
            "You are a product manager. Given a customer feedback cluster, "
            "write a focused one-page PRD. Return JSON only — no markdown, no explanation. Fields:\n"
            "- title: PRD title\n"
            "- problemStatement: 2-3 sentences on what is broken\n"
            "- userPersona: who is affected and in what context\n"
            "- businessImpact: specific impact on retention, revenue, or NPS\n"
            "- proposedSolution: concrete description of what to build\n"
            "- outOfScope: what explicitly NOT to build this iteration\n"
            "- successMetrics: array of exactly 3 measurable targets\n"
            "- timeline: '1 week', '2 weeks', or '1 month'"
        ),
        messages=[{"role": "user", "content": f"Here is the feedback cluster:\n\n{cluster_text}"}],
    )

    raw = _strip_fences(message.content[0].text)
    try:
        prd_data = json.loads(raw)
        return GeneratedPRD(**prd_data)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[generate_prd] Raw response: {raw}")
        raise HTTPException(status_code=500, detail=f"Failed to parse Claude response: {str(e)}")
