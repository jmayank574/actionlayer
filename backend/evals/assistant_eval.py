"""Golden-question eval for the Assistant (see golden_questions.yaml).

Runs each question through the real agent loop (real model calls -- costs
money, roughly a few cents per question) and applies deterministic checks
(evals/checks.py). The one that matters most: every number in an answer must
trace to a tool result. That's the project's "nothing is invented" rule,
checked automatically instead of trusted to a prompt.

Run (from backend/):
  python -m evals.assistant_eval                      # all cases
  python -m evals.assistant_eval --only biggest_problem,trend_pricing
  python -m evals.assistant_eval --limit 5            # first N, for a cheap smoke run

Exit code 1 if any `critical` case fails or the pass rate is below
--min-pass-rate (default 0.9 -- LLM output varies run to run, so demanding
100% on non-critical cases would just make the suite flaky).
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml
from anthropic import Anthropic
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent))
from assistant.agent import run_conversation
from assistant.tools import AssistantData
from evals import checks

load_dotenv(Path(__file__).parent.parent / ".env")

GOLDEN_PATH = Path(__file__).parent / "golden_questions.yaml"
RESULTS_PATH = Path(__file__).parent / "results" / "assistant_latest.json"
PROMPT_WORD_LIMIT = 130   # what agent.py's prompt asks for -> anything over is a warning
DEFAULT_MAX_WORDS = 180   # hard failure ceiling: real slack over the prompt limit, since model output varies run to run


def _scopes_from_trace(trace: list[dict]) -> set[str]:
    """Which source scopes the answer was actually built from. A stats/timeseries
    call with no scope means the default (combined_overlap); a review search
    filtered to one source counts as evidence for that source."""
    scopes: set[str] = set()
    for call in trace:
        inp = call["input"]
        if call["name"] in ("get_category_stats", "get_trend_timeseries"):
            scopes.add(inp.get("scope") or "combined_overlap")
        elif call["name"] == "search_reviews" and inp.get("source"):
            scopes.add(inp["source"])
    return scopes


def evaluate_case(case: dict, resp: dict, data: AssistantData) -> tuple[list[str], list[str]]:
    """Returns (failures, warnings) for one case's response."""
    expect = case.get("expect", {})
    text = resp["text"]
    trace = resp.get("tool_trace", [])
    relaxed = expect.get("format") == "relaxed"
    failures: list[str] = []
    warnings: list[str] = []

    # --- always-on format/integrity checks ---
    if checks.has_emoji(text):
        failures.append("contains emoji")
    if checks.banned_phrases_found(text):
        failures.append(f"banned phrasing: {checks.banned_phrases_found(text)}")
    if not relaxed:
        if checks.has_markdown_header(text):
            failures.append("uses markdown headers")
        if checks.has_table(text):
            failures.append("uses a table")
        if checks.leaks_review_id(text):
            failures.append("leaks a review id into the prose")
        words = checks.word_count(text)
        max_words = expect.get("max_words", DEFAULT_MAX_WORDS)
        if words > max_words:
            failures.append(f"{words} words (max {max_words})")
        elif words > PROMPT_WORD_LIMIT:
            warnings.append(f"{words} words (prompt limit is {PROMPT_WORD_LIMIT})")

    # --- grounding: every statistic must trace to a tool result ---
    prior_assistant = tuple(m["content"] for m in case.get("messages", []) if m["role"] == "assistant")
    bad = checks.ungrounded_claims(text, trace, extra_texts=prior_assistant)
    if bad:
        failures.append("ungrounded numbers: " + ", ".join(sorted({c.raw.strip() for c in bad})))

    # --- quotes must be real reviews, verbatim ---
    known = dict(zip(data.tagged["review_id"].astype(str), data.tagged["text"]))
    for q in resp.get("quotes", []):
        real = known.get(str(q["review_id"]))
        if real is None:
            failures.append(f"quote for nonexistent review_id {q['review_id']}")
        elif q["text"] != real[:600]:
            failures.append(f"quote text differs from real review {q['review_id']}")

    # --- per-case expectations ---
    tools_used = [c["name"] for c in trace]
    if expect.get("tools_all"):
        missing = [t for t in expect["tools_all"] if t not in tools_used]
        if missing:
            failures.append(f"did not call required tool(s): {missing}")
    if expect.get("tools_any") and not any(t in tools_used for t in expect["tools_any"]):
        failures.append(f"called none of {expect['tools_any']} (used {sorted(set(tools_used)) or 'no tools'})")
    if expect.get("scopes_used"):
        missing = [s for s in expect["scopes_used"] if s not in _scopes_from_trace(trace)]
        if missing:
            failures.append(f"never queried scope(s) {missing} (queried {sorted(_scopes_from_trace(trace))})")
    if expect.get("chart") is True and not resp.get("chart"):
        failures.append("expected a chart, got none")
    if expect.get("chart") is False and resp.get("chart"):
        failures.append("returned a chart where none should exist")
    if expect.get("quotes_min", 0) > len(resp.get("quotes", [])):
        failures.append(f"only {len(resp.get('quotes', []))} quote(s), expected >= {expect['quotes_min']}")
    if expect.get("recommendation") and not relaxed and not checks.has_recommendation(text):
        failures.append("missing the closing **Recommendation:** line")
    if expect.get("refusal") and not checks.looks_like_refusal(text):
        failures.append("should have declined (data can't answer this) but didn't")

    return failures, warnings


def run_case(case: dict, data: AssistantData, client: Anthropic) -> dict:
    messages = case.get("messages") or [{"role": "user", "content": case["question"]}]
    started = time.time()
    try:
        resp = run_conversation(data, client, messages, include_trace=True)
    except Exception as e:  # a crash is a failure of the system under test, not of the harness
        return {"id": case["id"], "critical": bool(case.get("critical")), "passed": False,
                "failures": [f"crashed: {type(e).__name__}: {e}"], "warnings": [], "seconds": round(time.time() - started, 1)}
    failures, warnings = evaluate_case(case, resp, data)
    return {
        "id": case["id"], "critical": bool(case.get("critical")), "passed": not failures,
        "failures": failures, "warnings": warnings, "seconds": round(time.time() - started, 1),
        "words": checks.word_count(resp["text"]),
        "tools": [c["name"] for c in resp.get("tool_trace", [])],
        "answer": resp["text"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="comma-separated case ids")
    parser.add_argument("--limit", type=int, help="run only the first N cases")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--min-pass-rate", type=float, default=0.9)
    args = parser.parse_args()

    from evals.preflight import api_error
    problem = api_error()
    if problem:
        print(f"ERROR: the eval makes real model calls, but the API isn't usable: {problem}", file=sys.stderr)
        return 2

    cases = yaml.safe_load(GOLDEN_PATH.read_text(encoding="utf-8"))
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        print("No cases selected.", file=sys.stderr)
        return 2

    data = AssistantData()
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    print(f"Running {len(cases)} golden question(s) against {len(data.tagged)} reviews...\n")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda c: run_case(c, data, client), cases))

    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        crit = " [critical]" if r["critical"] else ""
        print(f"{mark}{crit}  {r['id']}  ({r['seconds']}s, {r.get('words', '?')} words)")
        for f in r["failures"]:
            print(f"      x {f}")
        for w in r["warnings"]:
            print(f"      ! {w}")

    passed = sum(r["passed"] for r in results)
    rate = passed / len(results)
    critical_failed = [r["id"] for r in results if r["critical"] and not r["passed"]]
    print(f"\n{passed}/{len(results)} passed ({rate:.0%}). Critical failures: {critical_failed or 'none'}")

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps({"pass_rate": rate, "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Full answers + traces: {RESULTS_PATH}")

    return 1 if (critical_failed or rate < args.min_pass_rate) else 0


if __name__ == "__main__":
    sys.exit(main())
