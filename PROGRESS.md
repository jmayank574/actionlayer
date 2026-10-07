# ActionLayer — progress tracker

Goal: a better product first, then scale it. Updated after every step.
Legend: [x] done · [~] built, not yet verified/committed · [ ] not started

## Roadmap (agreed build order)

| # | Step | Status |
|---|------|--------|
| 1 | **Evals** — tagger regression gate + Assistant golden questions | [x] **done** — pushed, green in CI end to end |
| 2 | **Pipeline health agent** — deterministic daily checks + LLM diagnosis → GitHub issue | [x] **done** — pushed; CI `--post-issue` path still unexercised (no `gh` locally) |
| 3 | **UI QA agent** — Playwright screenshots + text checks + vision pass, in CI | [x] **done** — pushed; CI `--post-issue` path still unexercised locally |
| 4 | **Semantic search over reviews** — also clusters the ~20% "Other" bucket into proposed subcategories | [x] **done** — pushed |
| 5 | **Onboarding agents for product #2** — source discovery, taxonomy drafting, eval bootstrap (all via PR, human approves) | [x] **done** — pushed; Oura Ring run committed as a demo, not a product-#2 decision |

## Step 2 — Pipeline health agent (in detail)

- [x] `backend/ops/health_check.py` -- deterministic checks (step outcomes, ingestion issues, tag failures) + one Claude call that explains real findings in plain English, never decides what's wrong. Falls back to a plain listing if the API isn't reachable.
- [x] Deliberately does NOT alert on Other/Ungrouped or multi-label drift -- those are chronic, already-tracked conditions (see Open items below), not something a given day's run broke. Alerting on them daily would just train you to ignore the check.
- [x] `backend/ingest.py` now writes `data/ingest_run_stats.json` (machine-readable, parallel to the human-readable `data/README.md`) so the health check doesn't parse markdown prose.
- [x] `.github/workflows/daily-pipeline.yml` -- added `id:` to each step, `issues: write` permission, and a final `if: always()` health-check step wired to real step outcomes.
- [x] Verified locally: a real stale finding (8 tag failures from the pre-pin SDK bug) surfaced correctly; fallback path (no API key) and the real Claude diagnosis call both tested; dry-run issue preview formats correctly.
- [ ] `--post-issue`'s actual `gh issue create`/`list` calls not tested locally (no `gh` CLI on this dev machine) -- only exercised for real in CI.
- [x] Reviewed and pushed.

## Step 3 — UI QA agent (in detail)

- [x] `frontend/tests/ui_qa.spec.ts` (Playwright) -- drives the real dev server through the golden path: landing page → category → product dashboard → Explore tab (category breakdown, watch categories, trend chart) → review drawer with real review text. Tracks console errors/pageerrors throughout; any console error fails the run.
- [x] `frontend/playwright.config.ts` -- auto-starts `npm run dev`, screenshots every step, traces on failure.
- [x] `backend/ops/ui_qa_diagnose.py` -- parses Playwright's JSON report; on a failure, sends the real failure screenshot(s) to Claude (vision) for a plain-English explanation, then files a GitHub issue. Same explain-don't-decide split as `health_check.py` -- Playwright's own assertions are the only thing that decides pass/fail.
- [x] `.github/workflows/ui-qa.yml` -- runs the suite on push/PR touching `frontend/**`; only calls the paid diagnosis step if the suite actually failed.
- [x] Verified locally: both tests pass against the real dev server and real exported WHOOP data (review drawer screenshot showed real, current reviews). Deliberately broke a selector to produce a real failure and confirmed the vision diagnosis correctly identified the page was fine and the *test* was wrong -- it didn't just assume the app was broken.
- [x] Reviewed and pushed.

## Step 4 — Semantic search + Other-bucket clustering (in detail)

- [x] `backend/semantic/embeddings.py` -- local `sentence-transformers` (all-MiniLM-L6-v2) embeddings, cached incrementally by review_id in `data/review_embeddings.npz`. Picked over a paid embeddings API (OpenAI/Voyage) specifically so the pipeline still needs only `ANTHROPIC_API_KEY`, no second credential. Kept out of `requirements.txt` (separate `requirements-semantic.txt` -- torch is a ~2GB dependency, not needed by the daily pipeline, Assistant, or evals).
- [x] `backend/semantic/search.py` -- semantic search over real reviews by meaning, not just keyword match. CLI: `python -m semantic.search "<query>"`. Verified: "battery draining overnight" correctly surfaced real reviews about battery drain with no literal keyword overlap required.
- [x] `backend/semantic/cluster_other.py` -- KMeans clusters the Other/Ungrouped bucket (deterministic, decides grouping); one Claude call proposes a name + definition per cluster from real representative reviews (explains, doesn't decide membership). Writes `data/other_cluster_proposals.md`/`.json` -- a proposal only, never edits `taxonomy.yaml`.
- [x] **Real finding from the first run**: 11 of 12 clusters (94% of the 733-review Other/Ungrouped bucket) are generic positive praise ("best fitness tracker," "X years and still love it") with nowhere to land -- not missing negative-complaint topics. Confirms the known gap ("only 3 of 13 categories have a dedicated positive subcategory," below) with hard evidence instead of a hunch. Only 1 cluster (45 reviews, 6%) was genuinely too terse/mixed to name.
- [x] Deliberately NOT wired into the live Assistant backend (`assistant_server.py`) -- same ~2GB dependency concern, would strain Render's free tier. Semantic search stays a separate, offline/on-demand tool.
- [ ] Decide whether to act on the cluster-proposal finding (e.g. add dedicated positive subcategories) -- open item, your call.
- [x] Reviewed and pushed. Open: whether to act on the clustering finding (below).

## Step 5 — Onboarding agent for product #2 (in detail)

- [x] `backend/onboarding/onboard_product.py` -- reuses the exact same building blocks already proven on WHOOP (`ingestion/google_play.py`, `ingestion/app_store.py`, `ingestion/normalize.py`, `ingestion/merge.py`, `sample_for_taxonomy.py`'s `stratified_sample`), generalized to take a product name/category/store ids instead of being WHOOP-hardcoded.
- [x] Pipeline: ingest real reviews → stratified open-coding sample → one Claude call drafts a bottom-up taxonomy (same YAML schema as `taxonomy.yaml`, citing real `sample_id`s per subcategory so a reviewer can check every category against the actual reviews that led to it) → carves out an unlabeled eval seed for a human to hand-label later → one consolidated onboarding report.
- [x] Everything lands under `backend/data/products/<slug>/`, fully isolated -- never touches WHOOP's `data/*.csv` or `data/taxonomy.yaml`, never runs the tagger. Turning a draft into a live taxonomy is a deliberate, separate, human step.
- [x] **Verified with a real run** against Oura Ring (`com.ouraring.oura` / App Store id 1043837948): 8,706 real reviews ingested, 60-review stratified sample, a 10-category/33-subcategory draft taxonomy grounded in real sample citations, 40-review unlabeled eval seed. Confirmed WHOOP's live data files were untouched by the run.
- [ ] Review the Oura Ring draft output (or discard it -- it's a demo of the pipeline, not a commitment to add Oura Ring as product #2) before deciding whether/how to commit `backend/data/products/`.
- [x] Reviewed and pushed. Oura Ring draft kept as a demo, not a product-#2 decision.

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
- [ ] **You:** decide whether to act on the Other/Ungrouped clustering finding (dedicated positive subcategories) -- see Step 4
- [ ] CI's `--post-issue` path (actual `gh issue create`) for both the health check and UI QA diagnosis has not been exercised for real yet -- only tested locally in dry-run mode (no `gh` CLI on this dev machine)
- [ ] **You:** Render won't auto-pick-up the anthropic pin unless it redeploys -- check its dashboard; if it didn't auto-deploy from the push, trigger Manual Deploy once
- [x] ~~Decision — tagger randomness~~ **Resolved: temperature 0 (option A).** Note: the ~3,600 reviews already tagged were made at default randomness and are NOT being re-tagged (costly, not needed); only new reviews get temperature-0 tags. Applies to the daily pipeline as soon as `tagger.py` is pushed
- [ ] **You:** lower `GLOBAL_DAILY_LIMIT` on Render from 150 to ~40, and set a monthly spend limit in the Anthropic console
- [ ] Taxonomy drift: "Other/Ungrouped" 20% (reference 10–15%), multi-label 48.7% (reference 35–40%). Step 4 targets this
- [ ] Only 3 of 13 categories have a dedicated positive subcategory; sentiment is a whole-review star proxy, not per-topic
- [ ] Card badge logic ignores sentiment (e.g. red "Needs Attention" beside 52% positive on Feature Requests)
- [x] ~~Insight cards have no per-card recommended action~~ **Fixed 2026-10-06** -- deterministic `card_action()` template, shown on every Zone A card

## Log
- **2026-10-06** Dashboard UX pass: unified the severity badge vocabulary (`frontend/src/lib/severity.ts`) across InsightCard and WatchZone/WatchCategoryPanel -- they previously used two different visual languages for the same concept. InsightCard now leads with badge + scannable stat line before the prose, and shows a new deterministic recommended-action line. Explore tab reordered so Watch Categories + Rising & Falling (the actionable content) come before the full 13-row breakdown, which also got quick filter chips (All/Rising/Falling/Watch/Stable). Fixed two user-facing strings that leaked an internal filename ("see taxonomy.yaml watch_reason") into product copy. Tried a 2-column grid for Watch Categories + Rising & Falling first -- reverted after seeing it live, since the two sections have very different content heights and it left a large empty gap.
- **2026-10-06** Built steps 2-5 in one session (per your go-ahead to do 3-5 together, then review as a whole before pushing). Step 2: pipeline health agent (`backend/ops/health_check.py`). Step 3: UI QA agent (`frontend/tests/ui_qa.spec.ts`, `backend/ops/ui_qa_diagnose.py`). Step 4: semantic search + Other-bucket clustering (`backend/semantic/`) -- found that 94% of Other/Ungrouped is unplaced positive praise, not missing complaint topics. Step 5: onboarding agent (`backend/onboarding/onboard_product.py`) -- real-data-verified against Oura Ring. All reviewed live and pushed.
- **2026-10-06** Evals workflow run #3 (commit `ea92a56`, post-pin): **green end to end** -- `unit` and `llm-evals` both passed. Step 1 is done.
- **2026-10-06** First real CI run of `evals.yml`: free `unit` job passed; paid `llm-evals` job failed -- all 180 eval reviews failed to re-tag, even after retry. The script only logged review ids, not the actual error (fixed: `revalidate_prompt_fix.py` now prints distinct failure reasons). Real cause, once visible: `TypeError: Messages.create() got an unexpected keyword argument 'temperature'` -- `anthropic` was unpinned in `requirements.txt`, and a fresh install resolved to 1.11.0, which removed `temperature` entirely (replaced by `effort`). Not a credit or key problem (checked: local key works, balance $6.72). **This would have silently broken the live daily pipeline's next tagging run** (same unpinned install). Fixed by pinning `anthropic==0.120.2`, verified via a clean-room install. Render's existing deploy already has 1.8.0 (from its own earlier build) -- not currently broken (Assistant doesn't use `temperature`), but should be redeployed to pick up the pin.

- **2026-09-25** Evals built. Found by them: trend questions produced 385-word reports with tables/emoji and 5 chart-tool calls (wrong chart shown); answers averaged 183 words vs a 120 target (now hard 130); ratings rendered as emoji; "negative sentiment" phrasing slipped through; Assistant couldn't answer "how many reviews / how fresh" (added a dataset-summary tool). Backend now returns a clear 503 instead of a bare 500 when the model API fails.
- **2026-09-25** Applied the temperature-0 fix and re-verified with two more re-tag runs (see Step 1). Step 1 is now functionally complete; remaining: your review, then commit + push.
- **2026-09-25** Verification runs (after credit restored): full Assistant suite 19/20 (mean answer 135 words, down from 183; 0 ungrounded numbers). Tagger re-run exposed that tagging is non-deterministic (26% of reviews change tags between identical runs) and that the gate's tolerance/baseline were miscalibrated — the eval caught a flaw in itself and a real consistency problem in the pipeline.
- **2026-09-25** Incident: Anthropic credit ran out (eval runs likely drained it) → live demo returned errors and the paid tagger eval failed. Credit restored; local and live keys verified working.
