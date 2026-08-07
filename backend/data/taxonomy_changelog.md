# Taxonomy changelog — v1 → v2

Correction + interpretability pass over `data/taxonomy.yaml`. No new open
coding, no new sample, no full-dataset tagging happened in this pass — only
the specific full-dataset keyword checks noted under Fix 1, done to verify a
claim before acting on it rather than assuming it.

---

## Fix 1 — `ai_coach.ai_autonomy` / `customer_support` contradiction

**The problem:** `taxonomy_notes.md` (v1) said a review reading "customer
support is entirely AI now" should be tagged Customer Support. But
`taxonomy.yaml` (v1) listed the near-identical scenario — "every support
channel is now AI — email and chat — with no path to a human" — as an
`ai_autonomy` include example. Same real-world complaint, two different homes
in two different files.

**Verification before fixing:** searched the full 3,295-review dataset (not
just the 180-review sample) for both complaint shapes, since acting on an
assumed pattern without checking would just replace one guess with another.

- Shape A — "support is AI-only, can't reach a human": tight regex
  (`support.{0,25}(is|s).{0,10}ai`, `ai.{0,15}(support|response)`, "no way to
  reach/speak to a human", "replaced by AI", "AI bot/slop/gaslighting", "past
  the AI") returned 22 hits. Read all 22 in full. **20 were real matches** of
  this exact shape — support/billing/device problems where the reviewer
  explicitly says the channel is AI-only and no human is reachable. 2 were
  false positives from the regex (both 5-star reviews praising an "AI
  bot"/"health coach AI" — unrelated to support access).
- Shape B — "I disabled the AI Coach and it silently re-enabled itself":
  searched for `(disable|turn off|turned off).{0,40}(ai coach|coach)` across
  the full dataset. **1 match** — the same review already in the 180-review
  sample (the one that originally seeded the `ai_autonomy` subcategory).

So Shape A is real and common (20/3,295); Shape B is real but extremely rare
(1/3,295, and it's the same single review already known). They are not the
same complaint and don't belong in the same subcategory.

**Changes made:**

| Location | Old | New | Why |
|---|---|---|---|
| `ai_coach.ai_autonomy` includes | `"every support channel is now AI — email and chat — with no path to a human"` | *(removed)* | This was the contradiction. That shape is a support-channel complaint, not an AI Coach feature-control complaint. |
| `ai_coach.ai_autonomy` definition | "Users report being unable to disable the AI coach, **or that human support access has been replaced by AI-only channels**." | "Users report being unable to disable or opt out of the AI Coach feature itself... **not the support channel**." | Scope narrowed to match what the subcategory can actually defend with evidence. |
| `ai_coach.ai_autonomy` includes (new) | — | `"AI and community features are pushed on the user with no visible way to opt out or send feedback about it"` | Replaces the removed example with a real one from the 180-sample (originally coded here, unaffected by the fix) so the subcategory still has 2 concrete anchors. |
| `ai_coach.ai_autonomy` excludes | *(didn't mention customer_support)* | Added explicit line routing "support is AI-only" complaints to `customer_support > ai_only_support_channel`, even when the same review also separately complains about the AI Coach feature (both tags apply in that case). | Closes the gap that caused the contradiction in the first place. |
| `ai_coach` (parent) `watch_reason` | Cited "I can't turn it off" and "support is now only AI" together as the evidence. | Rewritten to state the corrected evidence: the "can't turn it off" shape is 1 match in the full dataset; "watch" means watch for more examples, not confirmed at scale. | The original watch_reason's evidence base is now split across two categories; overstating either one's support was misleading. |
| `customer_support` (parent) id | `id: customer_support`, name `Customer Support Quality` | name changed to `Customer Support Quality & Access` | The new subcategory is about *access* (is a human reachable at all), not just quality of an interaction that does happen — the old name undersold that. |
| `customer_support` — **new subcategory** | — | `ai_only_support_channel`: "The support channel itself has become AI-only, with no way to reach a human, independent of how fast or well the AI responds." 3 paraphrased includes drawn from the 20 real full-dataset matches; excludes drawn to distinguish from `support_responsiveness` (a human who's slow), `support_resolution_quality` (a human who's unhelpful), and `ai_coach > ai_autonomy` (the coaching feature itself). | Per the brief: fold into `support_responsiveness` or split out, decided by what's actually there. 20 real matches with a distinct shape (channel-access, not speed or correctness) justified a dedicated subcategory rather than folding into either existing one. |
| `customer_support.support_responsiveness` excludes | *(none)* | Added a line distinguishing "a human was slow" from "there is no human." | Without this, a tagger could reasonably put an AI-only complaint here too. |
| `customer_support.support_resolution_quality` excludes | Only mentioned `billing_disputes`. | Added a line routing "scripted AI response, no human alternative" here to `ai_only_support_channel` as well/instead. | Same reason — closes a second plausible mis-tag path. |
| `customer_support.support_satisfaction` excludes | `(none notable)` | Added a line pointing AI-Coach-specific praise to `ai_coach > ai_positive_reception`. | Found while fixing this section — praise for "the AI coaching" could otherwise land in either subcategory. |
| `ai_coach.ai_positive_reception` excludes | `(none notable)` | Added the reciprocal line pointing human-support praise to `support_satisfaction`. | Same reason, other direction. |
| `data/open_coding.csv`, sample_id 34 | tags: `AI.autonomy;CS.responsive;PB.value` | tags: `AI.autonomy;CS.ai_only_support_channel;PB.value` | This review ("I hate how bad the AI coach is and that you can't disable it... customer support is entirely AI") is the one that seeded the original contradiction. Its `AI.autonomy` tag is still correct (it does also complain about the coach itself). Its `CS.responsive` tag is upgraded to the new, more precise tag for the "AI-only, no human" half of the complaint. Not new coding — a relabel to match the corrected taxonomy. |
| `data/open_coding.csv`, sample_id 77 | tags: `HW.strap;CS.resolution;PB.billing` | tags: `HW.strap;CS.ai_only_support_channel;PB.billing` | Review text: "the AI support is appalling... no way to speak to a human." Matches the new subcategory more precisely than the generic resolution-quality tag it had. |

**Not changed:** `data/taxonomy_sample.csv` (unaffected — sampling wasn't
redone) and no other `open_coding.csv` rows (only these 2 of 180 used language
matching the old contradictory example closely enough to warrant a relabel).

---

## Fix 2 — full self-consistency pass on the 5 flagged pairs

| Pair | Verdict | Change |
|---|---|---|
| `app_stability` vs `sync_connectivity.data_sync_delays` | Already cross-referenced correctly in both directions. Tightened anyway. | Added a clause to the `app_stability` parent definition clarifying that "Performance" in its name means the app's *own* responsiveness, not latency caused by waiting on data — a "laggy" review with no other signal should default to `data_sync_delays`. Neither subcategory previously said this explicitly. |
| `data_accuracy.metric_accuracy` vs `health_signal_reliability` | **Real gap, not just borderline.** `health_signal_reliability`'s subcategories pointed to `data_accuracy`, but `metric_accuracy` never pointed back — a one-directional boundary. | Added an exclude line to `metric_accuracy` routing cardiac/ECG/BP-flavored complaints to `health_signal_reliability`. |
| `pricing_billing.price_value_perception` vs `pricing_billing.billing_disputes` | Already clean, symmetric, cross-referenced. | No change. |
| `sleep_tracking.sleep_alarm_ui` vs `ui_ux.redesign_regression` | **Real gap.** `sleep_alarm_ui`'s exclude only disambiguated from `sleep_accuracy`, never from `redesign_regression` — even though both of its own include examples ("alarm setting moved after a redesign") are redesign-caused. | Added reciprocal rule to both: sleep/alarm-specific confusion tags `sleep_alarm_ui` first even when redesign-caused; tag `redesign_regression` too only if the review names broader navigation changes beyond sleep/alarm. |
| `hardware_wearability.build_quality_perception` vs `hardware_wearability.strap_clasp_durability` | Already clean, symmetric, cross-referenced. | No change. |

**A second real overlap found during this pass** (not one of the 5 listed,
but the same severity as the sleep/redesign gap): `ui_ux.device_rendering_bugs`
vs. `platform_parity.android_specific_bugs`. Every `device_rendering_bugs`
example in the 180-sample (foldable phones, an Android accessibility setting)
happened to occur on an Android device, and neither subcategory said anything
about how to tell a form-factor/accessibility bug apart from a "the review
frames this as Android losing out to iOS" bug — a tagger hitting a real
foldable-phone rendering complaint would have no rule to follow. Added an
explicit rule to both: tag by what the review is actually complaining about
(screen size/accessibility vs. explicit Android-vs-iOS framing), not by which
OS the device runs, with both tags allowed when a review does both.

---

## Fix 3 — interpretability pass

**Definitions/excludes tightened** (found by asking, for every subcategory,
"could a reader confuse this with its nearest neighbor," not just re-reading
the 5 pairs above):

- `hardware_wearability.battery_life` — added exclude distinguishing the
  wearable's own battery from the WHOOP *app* draining the *phone's* battery
  (the latter is `app_stability`, not hardware).
- `app_stability.update_failures` — added cross-reference: an update failure
  during first-time setup should also be tagged `sync_connectivity >
  onboarding_pairing`.
- `sync_connectivity.onboarding_pairing` — added the reciprocal note.
- `sync_connectivity.ongoing_disconnects` — was `(none notable)`; added the
  reciprocal boundary against `onboarding_pairing` (first-ever pairing failure
  vs. a previously-working pairing dropping).
- `ai_coach.ai_reliability_bugs` — was `(none notable)`; added a line
  clarifying that an AI-Coach-caused app restart still belongs here, not
  `app_stability`, since the AI feature is the root cause.
- `ui_ux.redesign_regression` — was `(none notable)`; added the sleep/alarm
  boundary (see Fix 2).
- `ui_ux.feature_ui_friction` — was `(none notable)`; added exclude
  distinguishing "exists but awkward to use" (here) from "doesn't exist at
  all" (`feature_requests.missing_activity_types`).
- `feature_requests.missing_activity_types` — added the reciprocal line.
- `feature_requests.missing_metrics` — was `(none notable)`; added exclude for
  the case where a metric exists but is simply hard to find (a `ui_ux`
  findability issue, not a missing metric).
- `feature_requests.third_party_integration` — was `(none notable)`; added
  exclude distinguishing "WHOOP's own data is wrong" (`data_accuracy`) from
  "WHOOP's data is right but an external platform mishandles it" (here).
- `health_signal_reliability.ecg_bp_feature_reliability` — was
  `(none notable)`; added explicit exclude to `data_accuracy.metric_accuracy`
  for generic (non-ECG/BP) accuracy skepticism.
- `ui_ux.notification_community_issues` — was `(none notable)`; added exclude
  distinguishing a malfunctioning notification/community feature (here) from
  AI/community features being force-pushed with no opt-out
  (`ai_coach.ai_autonomy`).
- `platform_parity.android_feature_gaps` — was `(none notable)`; added exclude
  distinguishing "missing on Android specifically, present on iOS" (here) from
  "missing on both platforms" (`feature_requests`).
- `localization.missing_language_support` — was `(none notable)`; added a note
  that a missing language is technically a missing feature but stays here
  rather than `feature_requests`, since Localization exists as its own parent
  specifically because it's a distinct, recurring root cause.

Every subcategory that had `(none notable)` in v1 was re-checked; all of them
turned out to have a real plausible confusion once checked properly — none
were left as `(none notable)` in v2.

**Naming changes:**

- **`sync_connectivity` parent renamed** from "Bluetooth Pairing & Sync" to
  "Device Connectivity & Data Sync." This is the exact example the brief
  raised: `data_sync_delays` is about stale/missing *data*, not the Bluetooth
  *link* — the old name only described one of its three subcategories
  accurately.
- **`customer_support` parent renamed** from "Customer Support Quality" to
  "Customer Support Quality & Access," to cover the new
  `ai_only_support_channel` subcategory, which is about whether a human is
  reachable at all, not the quality of an interaction that does happen.
- Checked every other parent and subcategory name against its actual scope
  (`ai_coach`, `data_accuracy`, `health_signal_reliability`,
  `app_stability` — its "Performance" half is addressed via the parent
  definition rather than a rename, see Fix 2 table above, since no
  subcategory needed to change). No further renames were needed.

---

## Not done in this pass (out of scope per the brief)

- No new parent or subcategory beyond `ai_only_support_channel`, which exists
  specifically to resolve Fix 1.
- No new open-coding sample.
- No tagging of the full 3,295-review dataset — the two full-dataset searches
  above were narrow, single-purpose keyword checks to verify Fix 1's premise
  before acting on it, not a tagging pass. Step 3 (full-dataset tagging)
  remains undone.

## File-level summary

- `data/taxonomy.yaml`: version 1 → 2. 13 parent categories (unchanged), 38 →
  **39 subcategories** (+`ai_only_support_channel`). Every subcategory now has
  a real `excludes` line — zero remaining `(none notable)`.
- `data/taxonomy_notes.md`: updated the AI Coach/Customer Support borderline
  entry, the AI Coach watch-category entry, and the provisional-subcategories
  list to reflect the corrected, full-dataset-verified evidence.
- `data/open_coding.csv`: 2 of 180 rows relabeled (sample_id 34, 77) — same
  reviews, same review count, more precise tag.
- `data/taxonomy_sample.csv`: unchanged.
