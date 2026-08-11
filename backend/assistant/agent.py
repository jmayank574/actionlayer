"""Tool-calling loop for the Assistant: Claude reasons across multiple real
tool calls (search reviews, pull stats, get a time series) before answering,
same shape as Unwrap's Assistant ("reasons across your data" vs. a single
retrieval pass). Every fact in the final answer traces back to a tool result;
the system prompt forbids stating anything the tools didn't return.
"""

import json

from anthropic import Anthropic

from .tools import DEFAULT_SCOPE, AssistantData

MODEL = "claude-sonnet-4-6"
MAX_TOOL_ITERATIONS = 6
MAX_TOKENS = 900

SYSTEM_PROMPT = """You are the ActionLayer Assistant, answering questions about real WHOOP app reviews (Google Play + Apple App Store).

Grounding rules, non-negotiable:
- Never state a statistic, trend, or count you did not just get from a tool call in this conversation. If you don't have the data, call a tool -- don't estimate, round from memory, or recall general knowledge about WHOOP.
- Never quote or reference a review you did not retrieve via search_reviews in this conversation. Every quote must be traceable to a real review_id.
- If the data can't answer the question (e.g. it's about a competitor, or something outside these reviews), say so plainly instead of guessing.
- combined_overlap scope only covers Nov 2025 onward (when App Store data starts); google_play and app_store each have their own separate, longer history. Don't mix rates across scopes as if they were comparable -- state which scope a number is from when it matters. Default to combined_overlap unless the question specifically needs one source's longer history.
- A single review can carry multiple category tags -- it can be genuine evidence for more than one finding at once.

Answer format -- this is a chat panel someone scans in seconds, not a report:
- Lead with one bolded sentence that directly answers the question -- the headline finding, with its real number.
- Then 2-5 short bullets, each ONE line: a named driver plus its real stat (e.g. "**Crashes & freezes** -- 4.9% of recent reviews, down from 9.5%"). No sub-bullets, no nested detail.
- Do NOT quote review text or cite review_ids in your answer -- the UI already shows real customer quotes in a separate evidence panel next to your answer. Repeating them in prose is redundant. Just name the finding; the evidence panel carries the proof.
- End with one line starting "**Recommendation:**" -- the single most useful, concrete next action. Skip it only if the question isn't actionable (e.g. a pure lookup).
- No headers (##), no tables, no emojis, no restating the question, no "Here's a breakdown of...". If you're over ~120 words, you're writing a report instead of an answer -- cut it.
- This format is the default, not a hard cap: if the user explicitly asks for more depth, more quotes inline, a table, a longer breakdown, etc., give them that instead.

You have tools to list valid category ids, search real reviews, pull category rate/trend stats, and get a category's monthly time series for charting. Call list_categories first if you're not sure of the exact category_id for what's being asked -- don't guess an id.
"""

TOOLS = [
    {
        "name": "list_categories",
        "description": "List every taxonomy category and subcategory: id, name, level (parent/subcategory), and parent_id. Call this first if you don't already know the exact category_id for what the user is asking about.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_reviews",
        "description": "Full-text search over real tagged reviews. Returns up to `limit` matching reviews with review_id, source, rating, date, text, and category tags. Use this to find verbatim evidence for a finding.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keywords to search for in review text (all terms must appear, case-insensitive). Omit to browse by category/source/rating only."},
                "category_id": {"type": "string", "description": "Restrict to reviews tagged with this exact category or subcategory id."},
                "source": {"type": "string", "enum": ["google_play", "app_store"]},
                "min_rating": {"type": "integer"},
                "max_rating": {"type": "integer"},
                "limit": {"type": "integer", "description": "Max reviews to return. Default 10, hard cap 25."},
            },
        },
    },
    {
        "name": "get_category_stats",
        "description": "Get recent vs. baseline rate, percentage-point change, and verdict (spike/decline/stable) for one category, or every category if category_id is omitted, at a given source scope.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category_id": {"type": "string", "description": "Omit to get stats for every category."},
                "scope": {"type": "string", "enum": ["google_play", "app_store", "combined_overlap"], "description": "Defaults to combined_overlap."},
            },
        },
    },
    {
        "name": "get_trend_timeseries",
        "description": "Get the monthly/multi-month rate time series for one category, for charting.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category_id": {"type": "string"},
                "scope": {"type": "string", "enum": ["google_play", "app_store", "combined_overlap"]},
            },
            "required": ["category_id"],
        },
    },
]


def _run_tool(data: AssistantData, name: str, tool_input: dict):
    if name == "list_categories":
        return data.list_categories()
    if name == "search_reviews":
        limit = tool_input.get("limit") or 10
        return data.search_reviews(
            query=tool_input.get("query"), category_id=tool_input.get("category_id"),
            source=tool_input.get("source"), min_rating=tool_input.get("min_rating"),
            max_rating=tool_input.get("max_rating"), limit=limit,
        )
    if name == "get_category_stats":
        return data.category_stats(
            category_id=tool_input.get("category_id"), scope=tool_input.get("scope") or DEFAULT_SCOPE,
        )
    if name == "get_trend_timeseries":
        return data.trend_timeseries(
            category_id=tool_input["category_id"], scope=tool_input.get("scope") or DEFAULT_SCOPE,
        )
    return {"error": f"unknown tool {name}"}


def run_conversation(data: AssistantData, client: Anthropic, messages: list[dict]) -> dict:
    """messages: [{role: 'user'|'assistant', content: str}, ...], ending in the
    new user question. Returns {text, quotes, chart, category_stats}."""
    working_messages: list[dict] = [dict(m) for m in messages]
    quotes_by_id: dict[str, dict] = {}
    chart = None
    stats_used: list[dict] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, system=SYSTEM_PROMPT,
            tools=TOOLS, messages=working_messages,
        )

        if response.stop_reason != "tool_use":
            text = "".join(b.text for b in response.content if b.type == "text")
            return {
                "text": text,
                "quotes": list(quotes_by_id.values()),
                "chart": chart,
                "category_stats": stats_used,
            }

        working_messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result = _run_tool(data, block.name, block.input or {})

            if block.name == "search_reviews" and isinstance(result, list):
                for q in result:
                    quotes_by_id[q["review_id"]] = q
            if block.name == "get_trend_timeseries" and isinstance(result, list):
                chart = {
                    "category_id": block.input.get("category_id"),
                    "category_name": data.category_names.get(block.input.get("category_id"), block.input.get("category_id")),
                    "scope": block.input.get("scope") or DEFAULT_SCOPE,
                    "series": result,
                }
            if block.name == "get_category_stats" and isinstance(result, list):
                stats_used = result

            tool_results.append({
                "type": "tool_result", "tool_use_id": block.id,
                "content": json.dumps(result, default=str),
            })
        working_messages.append({"role": "user", "content": tool_results})

    return {
        "text": "I wasn't able to finish researching this within the allotted steps -- try breaking your question into smaller parts.",
        "quotes": list(quotes_by_id.values()), "chart": chart, "category_stats": stats_used,
    }
