# WHOOP review trends — May–Jul 2026 vs. trailing baseline

Generated from `data/tagged_reviews.csv` (3,295 tagged reviews). Every number below is
labeled by source — **google_play** (9-year history, reliable trailing-12-month baseline),
**app_store** (only exists from Nov 2025 onward — Apple's public feed caps at ~500 recent
reviews, so its baseline is a shorter ~5.5 months), or **combined_overlap** (both sources
pooled, but only using data from Nov 2025 onward, so the comparison is fair). Numbers are
never mixed across a full-history google_play baseline and a recency-only app_store one —
see Methodology at the bottom for why that would manufacture false spikes.

The current partial month (Aug 2026, 5 days of data) is excluded from all comparisons below.

## Rising

**1. AI Coach is surging, and it's a genuine product-change story, not tagging noise —
watch category.**
`ai_coach` roughly doubled its share of reviews in every scope: google_play 5.3% → 10.1%
of reviews (1.9x, trailing-12mo baseline), app_store 7.3% → 14.7% (2.0x), combined 6.1% →
12.6% (2.1x). Reading the actual reviews confirms this is a real event, not drift: a
2026-06-09 review says outright *"The recent AI coach upgrade is excellent,"* and the
complaint side of the spike (`personalization_use_case_fit`, below) includes a reviewer
explicitly contrasting old vs. new: *"I don't like the new AI — it used to be data-driven,
focused on facts. Now the 'coach' is routinely berating me..."* Read together, this looks
like an AI Coach update shipped around June 2026 that most users like (`ai_positive_reception`
jumped from 1.8% → 6.3% of google_play reviews, 3.5x; 1.2% → 7.2% in app_store, 5.9x) but a
smaller group dislikes the new tone. This is the one watch category with a real trend this
period — flagged regardless of its rank because the brief for watch categories was never
about volume, it was about stakes, and a coaching-tone change reaching users is worth
knowing about even though nothing here is medical-adjacent.

**2. Feature Requests, driven by "this doesn't fit my situation" complaints.**
`feature_requests` rose google_play 7.3% → 14.3% (2.0x), combined 9.6% → 14.7% (1.5x). The
subcategory driving it is `personalization_use_case_fit` (google_play 2.7% → 7.6%, 2.8x;
app_store 2.4% → 5.8%, 2.4x) — largely the same AI Coach tone-change reaction described
above, plus a handful of unrelated "this doesn't work for my use case" reviews. Worth
reading as a companion to finding #1, not a separate root cause.

**3. Support resolution quality complaints, smaller but real (google_play).**
`support_resolution_quality` rose 3.8% → 6.3% of google_play reviews (1.7x, +2.5pp) — the
smallest of the three flagged rises, included because it cleared both the relative (1.5x)
and absolute (+2pp) thresholds, not because it's dramatic. Worth watching next period rather
than acting on immediately.

## Falling

**1. App stability is meaningfully better — across every source.**
`app_stability` dropped in all three scopes: google_play 14.0% → 8.4% (0.60x), app_store
11.6% → 4.1% (0.35x), combined 11.4% → 6.0% (0.53x). This is the strongest signal in the
whole report because it's consistent across two independently-collected sources with
different review populations — that's much harder to explain away as a fluke of one
platform's reviewer mix. Read a sample of the actual `crashes_freezes` reviews in both the
recent and baseline windows (google_play): both are genuine crash/freeze complaints (*"my
whoop app is not opening,"* *"consistently experiencing freezing issues"*), so the drop
reflects fewer real crash complaints, not a tagging artifact — there are simply fewer of
them, proportionally, in May–Jul 2026 than in the trailing year.

**2. Billing disputes and cancellation friction are down.**
`billing_disputes` fell in google_play (10.5% → 6.3%, 0.60x) and sharply in app_store
(18.3% → 6.5%, 0.36x). The app_store drop is the single largest percentage-point move in
this report (−11.8pp) — genuinely worth flagging, but read it with more caution than the
app_stability finding: app_store's baseline window is only ~5.5 months (all the history it
has), so this is a shorter trend than google_play's 12-month comparison, and the actual
billing complaints in both windows are real and still serious (forced-renewal complaints,
"no way to stop monthly charges," survey-gated cancellation) — it's a rate drop, not a sign
the underlying billing UX problems are gone.

**3. Hardware/update-cycle friction easing (google_play).**
A cluster of related categories eased together in google_play: `hardware_wearability`
(5.4% → 2.9%, 0.54x), `update_failures` (4.1% → 2.1%, 0.51x), and
`notification_community_issues` (6.3% → 3.4%, 0.53x). Grouped here because they moved in
the same direction over the same window, not because they share a root cause — worth a
second look next period to see if this holds.

## Watch categories, checked explicitly

- **ai_coach**: real spike, covered above as finding #1.
- **health_signal_reliability**: **no spike.** google_play doesn't clear the
  minimum-occurrence bar (2 recent mentions against the 5-mention floor). combined_overlap
  clears the volume floor fine (8 recent mentions) and shows a real rate drop — 2.65% →
  1.51% of reviews, a ratio of 0.57 that clears the 0.67 relative-decline threshold — but
  the absolute move (−1.14pp) falls short of the 2pp floor, so it correctly comes back
  "stable" rather than flagged; it's a real but small drop, not a volume problem. app_store
  shows a *decline* (4.9% → 2.1%, 6 recent mentions — barely over the floor), but at that
  volume it's not a number to act on, just one to keep an eye on. Nothing alarming to
  report this period.

## Sanity checks performed

Read actual review text (not just the aggregated numbers) for three of the flagged results
before finalizing this report:

1. **`ai_positive_reception` / `personalization_use_case_fit` spike (google_play, recent
   window)** — 6 reviews read from each. Confirmed genuine AI-Coach-specific content,
   including the explicit "recent AI coach upgrade" mention that anchors finding #1.
2. **`crashes_freezes` decline (google_play, recent vs. baseline)** — 5 reviews read from
   each window. Both contain real crash/freeze complaints; the drop is a real rate change,
   not a tagging artifact making old complaints disappear.
3. **`billing_disputes` decline (app_store, recent vs. baseline)** — 5 reviews read from
   each window. Both contain genuine billing/cancellation complaints (forced renewals, no
   in-app cancel path); confirms the drop is a real rate change but that the underlying
   problem is still present, just less frequent.

No sign of the source-coverage artifact this analysis was specifically built to avoid (a
category looking like it "spiked" purely because app_store data only starts existing in
late 2025) — every flagged app_store and combined_overlap result was cross-checked against
whether google_play showed the same direction, and the headline stories above are the ones
that either hold up in google_play alone or were read directly to confirm real content.

## Methodology

- **Rates, not counts.** Every number is % of that window's reviews carrying the tag, so
  the numbers aren't confounded by review-volume changes month to month.
- **Recent window**: trailing 3 complete months (May, Jun, Jul 2026). Current partial month
  (Aug 2026) excluded.
- **Baseline window**: trailing 12 months before the recent window, or all available prior
  history if a source has less than 12 months (app_store: ~5.5 months, all it has).
- **Spike/decline thresholds**: flagged only if the relative change is ≥1.5x (spike) or
  ≤0.67x (decline) of baseline **and** the absolute change is ≥2 percentage points in that
  direction. Both conditions guard against the two ways a threshold can mislead: relative-only
  would flag a category moving from 0.4% to 0.8% of reviews as "doubled" when it's noise;
  absolute-only would miss real proportional shifts in smaller categories.
- **Minimum volume, stated explicitly**: a category needs ≥5 occurrences in the recent
  window to be evaluated at all (below that, a single review swings the rate too much to
  trust), and the source needs ≥50 total reviews in its baseline window (below that, the
  baseline rate itself isn't reliable). Categories that don't clear these bars are marked
  `insufficient_recent_occurrences` or `insufficient_baseline_volume` in the data rather than
  silently omitted or force-flagged.
- **Descriptive time series bucketing** (`data/category_trends.csv`): monthly by default;
  where a source's month has under 30 total reviews, consecutive months are merged forward
  until the combined bucket reaches 30 (this mostly affects google_play's 2017–2018 data,
  which is too sparse for monthly reporting at any point in its history — those years appear
  as wide multi-month buckets, clearly marked `period_type = multi_month`, and should be read
  as rough historical context, not a reliable trend signal).
- **combined_overlap** pools google_play + app_store, but restricts both the recent AND
  baseline windows to Nov 2025 onward (when both sources actually have data) — never
  combining app_store's short history with google_play's full 9-year baseline, which is
  exactly the failure mode this analysis was built to avoid.

## Files

- `data/category_trends.csv` — full descriptive time series: period × source × category ×
  rate, with `adequate_volume`, `in_recent_window`, `flagged_spike`, `flagged_decline`
  columns. Built to be dashboard-ready without re-deriving anything.
- `data/category_trend_verdicts.csv` — the recent-vs-baseline comparison itself: one row
  per (scope × category) with recent/baseline counts, rates, percentage-point delta, ratio,
  and verdict. This is what the findings above are drawn from.
