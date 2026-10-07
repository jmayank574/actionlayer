"""Runs after the UI QA Playwright suite (frontend/tests/ui_qa.spec.ts),
whatever its outcome. Playwright's own assertions are the only thing that
decides pass/fail here -- a real selector, a real piece of exported data, a
real console.error. This script's only job, and only when something failed,
is to look at the failure screenshot and explain in plain English what's
visibly wrong, the same explain-don't-decide split as ops/health_check.py.

Run with (from backend/):
  python -m ops.ui_qa_diagnose                dry run -- prints the diagnosis,
                                               never calls the GitHub API
  python -m ops.ui_qa_diagnose --post-issue    also opens a GitHub issue
                                               (needs `gh` authenticated)

Reads frontend/tests/results/results.json (Playwright's JSON reporter
output) and the screenshot files its attachments point to.
"""

import argparse
import base64
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
RESULTS_PATH = FRONTEND_DIR / "tests" / "results" / "results.json"
ISSUE_LABEL = "ui-qa"


def _iter_specs(suite: dict):
    for spec in suite.get("specs", []):
        yield spec
    for sub in suite.get("suites", []):
        yield from _iter_specs(sub)


def collect_failures() -> list[dict]:
    """Plain parsing of Playwright's own verdicts -- no judgment calls here."""
    if not RESULTS_PATH.exists():
        return [{"title": None, "error": f"{RESULTS_PATH} is missing -- the UI QA suite may not have run.", "screenshot": None}]

    try:
        data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [{"title": None, "error": f"results.json couldn't be read: {type(e).__name__}: {e}", "screenshot": None}]

    failures = []
    for suite in data.get("suites", []):
        for spec in _iter_specs(suite):
            for test in spec.get("tests", []):
                if test.get("status") == "expected":
                    continue
                for result in test.get("results", []):
                    if result.get("status") in ("passed", "skipped"):
                        continue
                    error_msg = "; ".join(e.get("message", "") for e in result.get("errors", []))
                    screenshot = next(
                        (a.get("path") for a in result.get("attachments", []) if a.get("name") == "screenshot"),
                        None,
                    )
                    failures.append({"title": spec.get("title"), "error": error_msg, "screenshot": screenshot})
    return failures


def diagnose(failures: list[dict]) -> str:
    """One Claude call, vision-capable, given only the real failing screenshot
    + the real Playwright error for each failure -- it describes what it sees,
    it does not decide whether the run failed (Playwright already did)."""
    from evals.preflight import api_error
    problem = api_error()
    if problem:
        print(f"  (skipping AI diagnosis, API not usable: {problem})")
        return "\n".join(f"- {f['title'] or '(suite-level)'}: {f['error']}" for f in failures)

    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    content = [{
        "type": "text",
        "text": (
            "The ActionLayer dashboard's automated UI QA suite (Playwright) found failures below. "
            "For each one, a failure screenshot is attached where available. Write a short, plain-English "
            "summary (3-6 sentences total) of what's visibly wrong on screen and the single most useful "
            "first thing to check. Use ONLY what you can see in the screenshots and the error text; say so "
            "if a screenshot isn't conclusive. No markdown headers, no emoji.\n\n"
        ),
    }]
    for f in failures:
        content.append({"type": "text", "text": f"\nTest: {f['title'] or '(suite-level)'}\nError: {f['error']}"})
        shot = Path(f["screenshot"]) if f["screenshot"] else None
        if shot and shot.exists():
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64.b64encode(shot.read_bytes()).decode("ascii"),
                },
            })

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=500,
            messages=[{"role": "user", "content": content}],
        )
        return "".join(b.text for b in response.content if b.type == "text")
    except Exception as e:  # a diagnosis failure must not stop the issue from being filed
        print(f"  (AI diagnosis call failed: {type(e).__name__}: {e} -- falling back to plain findings)")
        return "\n".join(f"- {f['title'] or '(suite-level)'}: {f['error']}" for f in failures)


def _run_gh(args: list[str]):
    import subprocess
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=30)


def issue_already_open_today(repo: str) -> bool:
    today_tag = date.today().isoformat()
    try:
        result = _run_gh([
            "issue", "list", "--repo", repo, "--label", ISSUE_LABEL, "--state", "open",
            "--search", today_tag, "--json", "number", "--jq", "length",
        ])
    except Exception as e:
        print(f"  (couldn't check for an existing issue: {e} -- will try to create one anyway)")
        return False
    if result.returncode != 0:
        print(f"  (gh issue list failed: {result.stderr.strip()} -- will try to create one anyway)")
        return False
    return result.stdout.strip() not in ("", "0")


def build_issue_body(diagnosis: str, failures: list[dict], run_url: str | None) -> str:
    lines = [diagnosis.strip(), "", "---", "", "**Failing tests:**", ""]
    lines += [f"- {f['title'] or '(suite-level)'}: {f['error']}" for f in failures]
    if run_url:
        lines += ["", f"[View this run]({run_url})"]
    lines += ["", f"_Filed automatically by `ops/ui_qa_diagnose.py`, {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}._"]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-issue", action="store_true")
    args = parser.parse_args()

    print("Checking the UI QA suite's results...")
    failures = collect_failures()

    if not failures:
        print("All UI QA checks passed -- nothing to report.")
        return 0

    print(f"\n{len(failures)} failure(s):")
    for f in failures:
        print(f"  - {f['title'] or '(suite-level)'}: {f['error']}")

    print("\nAsking Claude to look at the failure screenshot(s)...")
    diagnosis = diagnose(failures)
    print(f"\n{diagnosis}\n")

    repo = os.getenv("GITHUB_REPOSITORY", "")
    run_id = os.getenv("GITHUB_RUN_ID")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}" if repo and run_id else None
    title = f"UI QA: {len(failures)} failure(s) found -- {date.today().isoformat()}"
    body = build_issue_body(diagnosis, failures, run_url)

    if not args.post_issue:
        print("--- DRY RUN: would open this issue ---")
        print(f"Title: {title}")
        print(body)
        return 1

    if not repo:
        print("GITHUB_REPOSITORY not set -- can't file an issue outside of GitHub Actions.", file=sys.stderr)
        return 1

    if issue_already_open_today(repo):
        print("An open issue for today already exists -- not filing a duplicate.")
        return 1

    result = _run_gh(["issue", "create", "--repo", repo, "--title", title, "--body", body, "--label", ISSUE_LABEL])
    if result.returncode != 0:
        print(f"Failed to create the issue: {result.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"Opened: {result.stdout.strip()}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
