"""Runs after the daily pipeline (ingest -> tag -> trends -> export), whatever
its outcome, and answers one question: did today's run actually work? Every
check here is plain, deterministic Python reading real files this run
produced -- the real incidents this project has hit (a missing dependency, a
timezone bug, App Store silently returning nothing, an SDK update breaking
tagging) were each found late, by a human noticing something looked off days
later. This exists to say so the same day, not catch it or fix it.

Claude's only job, and only when a deterministic check actually found
something: turn the real numbers into a short, readable explanation. It is
never shown anything it wasn't given here, and it never decides what counts
as a problem -- the checks above it do that. See evals/ for the parallel
discipline applied to the tagger and the Assistant.

Run with (from backend/):
  python -m ops.health_check                 dry run -- prints what it would
                                               do, never calls the GitHub API
  python -m ops.health_check --post-issue     also opens a GitHub issue if
                                               something's wrong (needs `gh`
                                               authenticated -- true in CI,
                                               not on a dev machine)

Step outcomes come in as env vars (STEP_INGEST, STEP_TAG, STEP_TRENDS,
STEP_EXPORT -- "success"/"failure"/"skipped"/"cancelled"), set by the
workflow from each step's own `id`. Default "success" so this runs
standalone for local testing without faking a whole pipeline run.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent.parent / "data"
STEP_NAMES = ["ingest", "tag", "trends", "export"]
ISSUE_LABEL = "pipeline-health"


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"__read_error__": f"{type(e).__name__}: {e}"}


def collect_findings() -> list[str]:
    """Plain checks, no AI -- these decide what counts as a problem."""
    findings: list[str] = []

    for step in STEP_NAMES:
        outcome = os.getenv(f"STEP_{step.upper()}", "success")
        if outcome not in ("success", "skipped"):
            findings.append(f"Pipeline step '{step}' finished with outcome '{outcome}', not success.")

    ingest_stats = _load_json(DATA_DIR / "ingest_run_stats.json")
    if ingest_stats is None:
        findings.append("ingest_run_stats.json is missing -- ingestion may not have run or didn't finish writing it.")
    elif "__read_error__" in ingest_stats:
        findings.append(f"ingest_run_stats.json couldn't be read: {ingest_stats['__read_error__']}")
    elif ingest_stats.get("issues"):
        for issue in ingest_stats["issues"]:
            findings.append(f"Ingestion reported an issue: {issue}")

    tag_stats = _load_json(DATA_DIR / "tag_run_stats.json")
    if tag_stats is None:
        findings.append("tag_run_stats.json is missing -- tagging may not have run or didn't finish writing it.")
    elif "__read_error__" in tag_stats:
        findings.append(f"tag_run_stats.json couldn't be read: {tag_stats['__read_error__']}")
    else:
        if tag_stats.get("failed", 0) > 0:
            findings.append(
                f"{tag_stats['failed']} review(s) failed to tag this run "
                f"(coverage {tag_stats.get('coverage_pct_this_run', '?')}%)."
            )
        # Other/Ungrouped and multi-label rate are chronic, already-tracked taxonomy
        # drift (see PROGRESS.md open items) -- not something a given day's run broke.
        # Flagging them here every single day would just be noise that trains you to
        # ignore this check. They're Step 4's job (taxonomy/semantic-search cleanup),
        # not pipeline health's.

    return findings


def _run_gh(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=30)


def issue_already_open_today(repo: str) -> bool:
    today_tag = date.today().isoformat()
    try:
        result = _run_gh([
            "issue", "list", "--repo", repo, "--label", ISSUE_LABEL, "--state", "open",
            "--search", today_tag, "--json", "number", "--jq", "length",
        ])
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  (couldn't check for an existing issue: {e} -- will try to create one anyway)")
        return False
    if result.returncode != 0:
        print(f"  (gh issue list failed: {result.stderr.strip()} -- will try to create one anyway)")
        return False
    return result.stdout.strip() not in ("", "0")


def diagnose(findings: list[str]) -> str:
    """One Claude call, given only the real findings above -- it explains,
    it does not discover. Falls back to a plain listing if the API isn't
    reachable, so a diagnosis failure never blocks the issue from being filed."""
    from evals.preflight import api_error
    problem = api_error()
    if problem:
        print(f"  (skipping AI diagnosis, API not usable: {problem})")
        return "\n".join(f"- {f}" for f in findings)

    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = (
        "The ActionLayer daily data pipeline ran today and these automated checks found problems. "
        "Write a short, plain-English summary (3-5 sentences) of what likely happened and the single "
        "most useful first thing to check -- for someone who didn't watch the run. Use ONLY the facts "
        "below; do not guess at causes not evidenced here, and say so if the cause isn't obvious from "
        "this list alone. No markdown headers, no emoji.\n\n"
        "Findings:\n" + "\n".join(f"- {f}" for f in findings)
    )
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in response.content if b.type == "text")
    except Exception as e:  # a diagnosis failure must not stop the issue from being filed
        print(f"  (AI diagnosis call failed: {type(e).__name__}: {e} -- falling back to plain findings)")
        return "\n".join(f"- {f}" for f in findings)


def build_issue_body(diagnosis: str, findings: list[str], run_url: str | None) -> str:
    lines = [diagnosis.strip(), "", "---", "", "**Raw findings:**", ""]
    lines += [f"- {f}" for f in findings]
    if run_url:
        lines += ["", f"[View this run]({run_url})"]
    lines += ["", f"_Filed automatically by `ops/health_check.py`, {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}._"]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-issue", action="store_true", help="actually open a GitHub issue if something's wrong (needs gh authenticated)")
    args = parser.parse_args()

    print("Checking today's pipeline run...")
    findings = collect_findings()

    if not findings:
        print("All checks passed -- nothing to report.")
        return 0

    print(f"\n{len(findings)} finding(s):")
    for f in findings:
        print(f"  - {f}")

    print("\nAsking Claude for a plain-English summary...")
    diagnosis = diagnose(findings)
    print(f"\n{diagnosis}\n")

    repo = os.getenv("GITHUB_REPOSITORY", "")
    run_id = os.getenv("GITHUB_RUN_ID")
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}" if repo and run_id else None
    title = f"Daily pipeline: {len(findings)} issue(s) found -- {date.today().isoformat()}"
    body = build_issue_body(diagnosis, findings, run_url)

    if not args.post_issue:
        print("--- DRY RUN: would open this issue ---")
        print(f"Title: {title}")
        print(body)
        return 1  # non-zero on real findings, even in dry run, so CI visibly flags the run

    if not repo:
        print("GITHUB_REPOSITORY not set -- can't file an issue outside of GitHub Actions.", file=sys.stderr)
        return 1

    if issue_already_open_today(repo):
        print("An open issue for today already exists -- not filing a duplicate.")
        return 1

    result = _run_gh([
        "issue", "create", "--repo", repo, "--title", title, "--body", body, "--label", ISSUE_LABEL,
    ])
    if result.returncode != 0:
        print(f"Failed to create the issue: {result.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"Opened: {result.stdout.strip()}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
