# ActionLayer — progress tracker

Goal: a better product first, then scale it. Updated after every step.
Legend: [x] done · [~] built, not yet verified/committed · [ ] not started

## Roadmap (agreed build order)

| # | Step | Status |
|---|------|--------|
| 1 | **Evals** — tagger regression gate + Assistant golden questions | [~] built & partly verified (see below) |
| 2 | **Pipeline health agent** — deterministic daily checks + LLM diagnosis → GitHub issue | [ ] |
| 3 | **UI QA agent** — Playwright screenshots + text checks + vision pass, in CI | [ ] |
| 4 | **Semantic search over reviews** — also clusters the ~20% "Other" bucket into proposed subcategories | [ ] |
| 5 | **Onboarding agents for product #2** — source discovery, taxonomy drafting, eval bootstrap (all via PR, human approves) | [ ] |

Rule for every agent: it proposes via PR/issue, you approve. Nothing edits taxonomy or data unattended.

## Step 1 — Evals (in detail)

- [x] Checkers for Assistant answers (number grounding, format rules, banned phrasing, refusals) — `backend/evals/checks.py`, 20 unit tests passing
- [x] 20 golden questions, 4 marked critical — `backend/evals/golden_questions.yaml`
- [x] Assistant eval runner — `backend/evals/assistant_eval.py`
- [x] Tagger regression gate on the 180 hand-labeled reviews; baseline recorded (sub micro-F1 0.637, parent 0.773, Other agreement 83.3%) and matches the original hand-written report — `backend/evals/tagger_eval.py`
- [x] Preflight check so evals fail fast with the real reason (e.g. no credit) — `backend/evals/preflight.py`
- [x] CI workflow (free tier always; paid tier only when prompts/tools/taxonomy/evals change) — `.github/workflows/evals.yml`
- [x] First full run (20 questions): 0 ungrounded numbers, all critical passed; found and fixed real problems (see log)
- [x] **Re-ran the full 20-question suite on the final prompt (2026-09-25): 19/20 pass, all 4 critical pass, 0 ungrounded numbers.** Only failure: `scope_compare` at 186 words (limit 180) — a two-source comparison running slightly long; left as-is rather than loosening the test
- [x] **Ran `tagger_eval --retag` (2026-09-25): gate FAILED on an unchanged prompt** — all four gated metrics ~0.04 below baseline (sub micro-F1 0.637 → 0.596). Not a real regression: comparing the two runs, 26% of reviews (46/180) got a different tag set, total tags equal (297 vs 298), changes scattered both ways. Cause: `tagging/tagger.py` sets no `temperature`, so tagging runs at the API default (random sampling)
- [x] **Fixed the tagger gate (2026-09-25).** (1) Set `temperature=0` in `tagging/tagger.py` — identical tag sets across repeat runs went 74% → 89%, and gated scores move ~0.01–0.02 between runs instead of ~0.04. (2) Baseline now comes only from a `--retag` run (like-for-like); the free mode is informational and never gates. (3) "Other/Ungrouped agreement" (only ~24 reviews, 1 review = 0.042) demoted from gate to warning. New baseline: sub micro-F1 0.613, parent 0.741, Jaccard 0.565. Gate on run 2 vs baseline: PASSED. Caveat: two data points — tolerance 0.03 has ~2× headroom over the observed noise, and ~11% of reviews still vary at temperature 0
- [ ] Review everything, then commit + push (nothing from this step is committed yet)

## Uncommitted right now
`backend/assistant/agent.py`, `backend/assistant/tools.py`, `backend/assistant_server.py`, `backend/tagging/tagger.py` (temperature=0), `frontend/src/lib/assistant.ts`, `CLAUDE.md`, `.gitignore`, `.github/workflows/evals.yml`, `backend/requirements-dev.txt`, `backend/evals/` (new), this file.
Note: the live demo still runs the previous code until these are pushed (including the friendly "temporarily unavailable" error message).

## Done before this step (context)
- [x] Real-data pipeline: Google Play + App Store ingestion (upsert, never overwrites), incremental Claude tagging, trend/velocity stats with strict source-scope discipline, static-JSON export
- [x] Daily automation on GitHub Actions (13:00 UTC): ingest → tag → trends → export → commit. Fixed the missing-`pyyaml` failure that broke it for days
- [x] Dashboard: Insights feed (priority cards + watch categories), Explore (category breakdown, rising/falling, full-text search, shared scope selector), current month shown as a hollow point
- [x] Sentiment proxy (% rated 4–5★ vs 1–2★) through the whole stack
- [x] Assistant: tool-calling agent over real data, concise structured answers, real quotes, charts on trend questions
- [x] Deployed free: Vercel (dashboard) + Render (Assistant) + UptimeRobot keep-alive; rate limits (15/hr per visitor, 150/day total)

## Open items (need a decision or your action)
- [x] ~~Decision — tagger randomness~~ **Resolved: temperature 0 (option A).** Note: the ~3,600 reviews already tagged were made at default randomness and are NOT being re-tagged (costly, not needed); only new reviews get temperature-0 tags. Applies to the daily pipeline as soon as `tagger.py` is pushed
- [ ] **You:** lower `GLOBAL_DAILY_LIMIT` on Render from 150 to ~40, and set a monthly spend limit in the Anthropic console
- [ ] Taxonomy drift: "Other/Ungrouped" 20% (reference 10–15%), multi-label 48.7% (reference 35–40%). Step 4 targets this
- [ ] Only 3 of 13 categories have a dedicated positive subcategory; sentiment is a whole-review star proxy, not per-topic
- [ ] Card badge logic ignores sentiment (e.g. red "Needs Attention" beside 52% positive on Feature Requests)
- [ ] Insight cards have no per-card recommended action (the Assistant does)

## Log
- **2026-09-25** Evals built. Found by them: trend questions produced 385-word reports with tables/emoji and 5 chart-tool calls (wrong chart shown); answers averaged 183 words vs a 120 target (now hard 130); ratings rendered as emoji; "negative sentiment" phrasing slipped through; Assistant couldn't answer "how many reviews / how fresh" (added a dataset-summary tool). Backend now returns a clear 503 instead of a bare 500 when the model API fails.
- **2026-09-25** Applied the temperature-0 fix and re-verified with two more re-tag runs (see Step 1). Step 1 is now functionally complete; remaining: your review, then commit + push.
- **2026-09-25** Verification runs (after credit restored): full Assistant suite 19/20 (mean answer 135 words, down from 183; 0 ungrounded numbers). Tagger re-run exposed that tagging is non-deterministic (26% of reviews change tags between identical runs) and that the gate's tolerance/baseline were miscalibrated — the eval caught a flaw in itself and a real consistency problem in the pipeline.
- **2026-09-25** Incident: Anthropic credit ran out (eval runs likely drained it) → live demo returned errors and the paid tagger eval failed. Credit restored; local and live keys verified working.
