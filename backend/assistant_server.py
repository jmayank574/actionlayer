"""Local-only dev server for the ActionLayer Assistant chat. This is the one
live backend component in the repo -- everything else in the v2 pipeline is
precomputed and served as static JSON. Deliberately local-dev-only for now
(see CLAUDE.md) -- no deployment/CORS-for-production concerns yet.

Run with: uvicorn assistant_server:app --reload --port 8001
(alongside `npm run dev` in frontend/, same as running any other pipeline step)
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from assistant.agent import run_conversation
from assistant.tools import AssistantData

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

_data = AssistantData()
_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class ChatMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    messages: list[ChatMessage]


@app.post("/api/ask")
def ask(req: AskRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    return run_conversation(_data, _client, messages)


@app.get("/api/health")
def health():
    return {"status": "ok", "reviews_loaded": len(_data.tagged)}
