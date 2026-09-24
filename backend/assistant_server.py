"""Backend for the ActionLayer Assistant chat. This is the one live backend
component in the repo -- everything else in the v2 pipeline is precomputed
and served as static JSON (see CLAUDE.md). Runnable locally (uvicorn
assistant_server:app --reload --port 8001) or deployed (e.g. Render) for a
public demo -- see the rate-limiting below, which exists specifically to
bound worst-case Anthropic spend if this is ever running somewhere reachable
by a link that gets passed around, not just localhost.

Local run: uvicorn assistant_server:app --reload --port 8001
(alongside `npm run dev` in frontend/, same as running any other pipeline step)
"""

import os
import time
from collections import defaultdict

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from assistant.agent import run_conversation
from assistant.tools import AssistantData

load_dotenv()

app = FastAPI()

# Origins allowed to call this from a browser. Comma-separated via env var so
# a deployed frontend's real domain can be added without a code change --
# defaults to local dev only. NOTE: this is not a security boundary by
# itself (CORS only restricts browser fetches, not curl/scripts hitting the
# API directly) -- the rate limiter below is the actual cost guardrail.
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
# Vercel gives one project several live URLs (the production alias plus a
# per-deployment one), so an exact-match list breaks on whichever one isn't
# listed. This pattern covers this project's Vercel domains by default.
_allowed_origin_regex = os.getenv("ALLOWED_ORIGIN_REGEX", r"https://actionlayer[a-z0-9-]*\.vercel\.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins if o.strip()],
    allow_origin_regex=_allowed_origin_regex,
    allow_methods=["POST"],
    allow_headers=["*"],
)

_data = AssistantData()
_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# --- Rate limiting -----------------------------------------------------
# This is a personal demo, not a product with paying users -- the point is a
# hard ceiling on worst-case Anthropic spend if the link gets shared or
# crawled, not fairness or precision. In-memory is fine: a single small
# instance, restarts reset the counters, that's an acceptable tradeoff for
# what this is.
PER_IP_HOURLY_LIMIT = int(os.getenv("PER_IP_HOURLY_LIMIT", "15"))
GLOBAL_DAILY_LIMIT = int(os.getenv("GLOBAL_DAILY_LIMIT", "150"))
MAX_MESSAGES_PER_REQUEST = 20  # caps a single request's own token cost, independent of request count

_ip_requests: dict[str, list[float]] = defaultdict(list)
_global_requests: list[float] = []


def _prune(timestamps: list[float], window_seconds: float) -> list[float]:
    cutoff = time.time() - window_seconds
    return [t for t in timestamps if t > cutoff]


def _check_rate_limit(client_ip: str) -> None:
    global _global_requests
    now = time.time()

    _global_requests = _prune(_global_requests, 86400)
    if len(_global_requests) >= GLOBAL_DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="This demo has hit its daily request limit. It's a personal project, not a "
                   "production service -- try again tomorrow, or reach out if you want to talk about it.",
        )

    ip_history = _prune(_ip_requests[client_ip], 3600)
    if len(ip_history) >= PER_IP_HOURLY_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit reached for this hour -- try again shortly.")

    ip_history.append(now)
    _ip_requests[client_ip] = ip_history
    _global_requests.append(now)


class ChatMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    messages: list[ChatMessage]


@app.post("/api/ask")
def ask(req: AskRequest, request: Request):
    if len(req.messages) > MAX_MESSAGES_PER_REQUEST:
        raise HTTPException(status_code=400, detail="Conversation too long for this demo -- start a new one.")

    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown").split(",")[0].strip()
    _check_rate_limit(client_ip)

    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    return run_conversation(_data, _client, messages)


@app.get("/api/health")
def health():
    return {"status": "ok", "reviews_loaded": len(_data.tagged)}
