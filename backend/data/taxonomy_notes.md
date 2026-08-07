# Taxonomy design notes — WHOOP, step 2

Method: read all 180 reviews in `data/taxonomy_sample.csv` (stratified by source x
rating x time period, seed 42), assigned raw open-coding tags per review in
`data/open_coding.csv`, then clustered tags upward into the 13 parent categories
in `data/taxonomy.yaml`. Nothing below was decided before reading the sample —
the keyword pass you supplied was used only as a rough prior to sanity-check
against afterward.

No tagging of the full 3,295-review dataset has happened. These numbers describe
the 180-review sample only, **except** where explicitly marked as a full-dataset
keyword check below (done only to resolve the ai_coach/customer_support
contradiction — see `data/taxonomy_changelog.md` for that correction pass).

## Coverage

- **180** reviews read and open-coded
- **19 reviews (10.6%)** landed in Other/Ungrouped — overwhelmingly short,
  undifferentiated praise ("5 out of 5 stars," "life changing," "best purchase
  ever") with no product surface or issue named to hang a tag on. A few thin
  negatives ("overall disappointing") also landed here. This is a first-pass
  taxonomy, not a claim of full coverage — 10.6% Other on read #1 is expected,
  not a bug in the method.
- **68 reviews (37.8%)** carried 2+ tags. Multi-label is structural, not an edge
  case: pricing, hardware, sync, and support complaints routinely show up
  together in the same paragraph (e.g. a device failure *and* a poor warranty
  interaction *and* a subscription-cost complaint, all in one review). The
  taxonomy and any future tagging pipeline must assign multiple category+
  subcategory pairs per review — forcing single-label would silently drop real
  signal on over a third of this sample.
- **93 reviews (51.7%)** were single-tag, **19 (10.6%)** were Other.

## What the keyword prior got right, and what it missed

Your keyword pass was a reasonable volume prior, but reading the actual text
surfaced real gaps:

- **Sleep tracking** was the prior's #2 bucket (~15% keyword volume) but only
  ~8% of tagged issues in this sample (15 of 180) actually center sleep as the
  core topic. A lot of "sleep" keyword hits turned out to be sleep mentioned in
  passing inside a longer accuracy or feature-list review, not sleep being the
  point of the review — this is the exact blurring effect the brief warned
  about, now confirmed with real numbers.
- **Platform Parity (Android vs iOS)** and **Localization / Language Support**
  weren't in your keyword list at all, yet each showed up in ~5% of this sample
  (9/180 each) with a clean, repeated, distinct root cause — Android is
  consistently under-invested relative to iOS, and Chinese/Russian/Arabic
  support is repeatedly requested. Both are now full parent categories.
- **Pricing & Billing** was the single largest bucket by tag count in the
  sample (41 tags across its 4 subcategories) — consistent with the prior's
  ~21% estimate, but the sample makes clear it's really two different problems
  with two different owners: people who think the *price* is too high
  (product/pricing decision) versus people who can't get billing to behave
  correctly (support/ops execution). Keeping these as separate subcategories
  matters for who would act on each.

## Borderline calls — where the boundary was genuinely hard

- **App Stability vs. Sync & Data Sync Delays.** Both can present as "the app
  doesn't work." The line drawn: if the app itself crashes, freezes, or won't
  open, it's App Stability; if the app runs fine but the *data* is stale,
  missing, or the device is wrongly marked "not worn," it's Sync. A few reviews
  (e.g. a journal entry silently failing to save) could plausibly sit on either
  side — tagged as App Stability here since the failure was a specific in-app
  action, not a connectivity symptom.
- **Data Accuracy vs. Health-Signal Reliability.** These are both "the number is
  wrong," and could have been one category. Kept separate deliberately: Health-
  Signal Reliability is reserved for cases where the metric carries medical
  weight (a diagnosed condition, ECG, blood pressure) — the stakes are
  categorically different from a wrong step count, even though the surface
  complaint looks similar.
- **AI Coach vs. Customer Support — corrected in v2.** v1 of this file said
  "customer support is entirely AI now" belongs to Customer Support, but
  `taxonomy.yaml` v1's `ai_autonomy` subcategory listed the same shape as its
  own include example — a direct contradiction between the two documents. Fixed
  in the v2 correction pass: `ai_autonomy` is now narrowed to only the AI Coach
  *feature* being un-disable-able; the support-channel shape has its own new
  subcategory, `customer_support > ai_only_support_channel`, confirmed against
  the full 3,295-review dataset (20 real matches, 2 keyword-search false
  positives excluded — see `data/taxonomy_changelog.md`, Fix 1, for the full
  writeup).
- **Pricing (upsell) vs. UI/UX.** In-app upsell prompts are visually a UI
  element, but the root cause is a monetization decision, not a design flaw —
  kept under Pricing & Billing for that reason.
- **Feature Requests (personalization/use-case fit) vs. Hardware (comfort/fit).**
  Both use the word "fit," but they're unrelated: one is about whether the
  *product philosophy* suits a non-elite-athlete user, the other is about
  whether the *physical band* stays on the wrist.

## Watch categories (flagged regardless of volume)

- **Health-Signal Reliability & Medical-Adjacent Trust** — only 2 of 180
  reviews (1.1%), but includes a user with a diagnosed heart-rhythm condition
  reporting zero detected incidents, and ECG reports taking over a day to
  process. This is the highest-stakes category in the taxonomy by consequence,
  not by volume, and should never be sorted below higher-volume/lower-stakes
  categories in any downstream dashboard or prioritization view.
- **AI Coach & Automated Guidance** — 10 of 180 (5.6%) touch AI Coach at all.
  Updated in v2: after separating out the support-channel shape (now its own
  Customer Support subcategory), the specific "I followed your instructions to
  disable this and it turned back on" complaint that motivated this watch
  category is thinner than originally stated — a full-dataset keyword check
  found exactly **1 match in all 3,295 reviews**. It's kept as a watch category
  regardless, per the brief's own instruction not to bury low-volume/high-
  severity signal, but "watch" now means watch for more examples specifically,
  not "already confirmed at scale."

## Deliberately thin / provisional subcategories

A few subcategories rest on very few examples in this 180-review sample and
should be treated as provisional until the full-dataset tagging pass in step 3
gives real volume: `plan_trial_structure` (2), `english_jargon_complexity` (2),
`android_specific_bugs` (2), `cardiac_detection_trust` (1),
`ecg_bp_feature_reliability` (1). None were dropped, per the brief's
instruction not to bury low-volume/high-severity signal — but their boundaries
may need revision once more examples surface.

`ai_autonomy` is now the thinnest subcategory in the whole taxonomy: 2 examples
in the 180-review sample (one narrowed-scope match, one adjacent "AI/community
features pushed with no opt-out" match), and only **1 confirmed match in the
full 3,295-review dataset** for its core "disabled it and it re-enabled itself"
shape (see `data/taxonomy_changelog.md`, Fix 1). Its new sibling,
`ai_only_support_channel`, is the opposite case — added with zero sample
evidence but 20 confirmed full-dataset matches, making it better-supported than
several subcategories that originated in the 180-review pass.

## Files

- `data/taxonomy_sample.csv` — the 180 sampled reviews (reproducible, seed 42;
  regenerate with `python sample_for_taxonomy.py`)
- `data/open_coding.csv` — per-review tags assigned during this pass, joinable
  on `sample_id` back to the sample file for auditing any tag against the
  actual review text
- `data/taxonomy.yaml` — the taxonomy itself: 13 parent categories, 39
  subcategories total, with a one-line definition, paraphrased include
  examples, and an explicit exclude/boundary note for every subcategory
- `data/taxonomy_changelog.md` — the v1 -> v2 correction pass: every change,
  old text vs. new text, and why
