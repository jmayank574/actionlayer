# Tagger evaluation report — WHOOP (step 3, Part 2)

Scored against `data/eval_sample.csv` — 180 reviews, disjoint from the 180-review sample used to build the taxonomy, never seen by the tagging prompt as few-shot material. Predictions pulled from `data/tagged_reviews_eval_candidate.csv` (candidate/updated prompt, eval-only re-tag).

## Headline metrics

- **Subcategory-level micro-F1**: 0.628 (precision 0.590, recall 0.672)
- **Subcategory-level macro-F1**: 0.599 (all 39 subcategories, zero-support ones counted) / 0.633 (only the 35 subcategories with at least 1 human-labeled example in this eval set)
- **Parent-level micro-F1**: 0.767 (precision 0.734, recall 0.803)
- **Parent-level macro-F1**: 0.705 / 0.763 (only the 12 parents with support in this eval set)
- **Multi-label exact-match rate** (subcategory set == human set exactly): 41.7%
- **Multi-label exact-match rate** (parent set): 55.6%
- **Mean per-review Jaccard similarity** (subcategory level, partial credit): 0.587
- **Other/Ungrouped agreement**: of 24 reviews the human left blank, the tagger also predicted zero tags on 20 (83.3%) and forced at least one tag onto 4 (16.7%)

## Methodology note on the ground truth

5 of 180 human labels (5 found via explicit "capped at N" language in `notes`) were deliberately capped at 3 tags even where the labeler's own notes say the review "spans" more issues — a conservative-labeling choice, not a taxonomy gap. This means some tagger "false positives" below are the tagger finding a real, additional, legitimate tag that the human chose not to record, not the tagger being wrong. This affects a small, identifiable slice of rows (visible in a few of the "Worst individual misses" below) — it is not the primary explanation for the broader precision gap, but it means precision numbers here are a slight underestimate of true tagger correctness.

## Per-subcategory precision / recall / F1

Sorted by support (human-labeled frequency in this eval set) descending. `support` = number of eval reviews the human tagged with this subcategory.

| Subcategory | Support | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| metric_accuracy | 36 | 19 | 0 | 17 | 100.0% | 52.8% | 0.691 |
| feature_ui_friction | 32 | 7 | 5 | 25 | 58.3% | 21.9% | 0.318 |
| price_value_perception | 20 | 19 | 9 | 1 | 67.9% | 95.0% | 0.792 |
| ongoing_disconnects | 18 | 16 | 2 | 2 | 88.9% | 88.9% | 0.889 |
| activity_detection | 13 | 5 | 0 | 8 | 100.0% | 38.5% | 0.556 |
| support_resolution_quality | 12 | 9 | 1 | 3 | 90.0% | 75.0% | 0.818 |
| billing_disputes | 12 | 11 | 3 | 1 | 78.6% | 91.7% | 0.846 |
| sleep_accuracy | 11 | 9 | 2 | 2 | 81.8% | 81.8% | 0.818 |
| crashes_freezes | 10 | 9 | 6 | 1 | 60.0% | 90.0% | 0.720 |
| update_failures | 10 | 5 | 3 | 5 | 62.5% | 50.0% | 0.556 |
| onboarding_pairing | 9 | 6 | 1 | 3 | 85.7% | 66.7% | 0.750 |
| sleep_satisfaction | 8 | 6 | 4 | 2 | 60.0% | 75.0% | 0.667 |
| data_sync_delays | 7 | 6 | 5 | 1 | 54.5% | 85.7% | 0.667 |
| missing_activity_types | 7 | 2 | 4 | 5 | 33.3% | 28.6% | 0.308 |
| ai_positive_reception | 6 | 5 | 1 | 1 | 83.3% | 83.3% | 0.833 |
| missing_metrics | 5 | 5 | 11 | 0 | 31.2% | 100.0% | 0.476 |
| personalization_use_case_fit | 4 | 1 | 9 | 3 | 10.0% | 25.0% | 0.143 |
| comfort_fit | 4 | 3 | 2 | 1 | 60.0% | 75.0% | 0.667 |
| build_quality_perception | 4 | 3 | 5 | 1 | 37.5% | 75.0% | 0.500 |
| ai_reliability_bugs | 4 | 4 | 2 | 0 | 66.7% | 100.0% | 0.800 |
| plan_trial_structure | 3 | 3 | 1 | 0 | 75.0% | 100.0% | 0.857 |
| support_satisfaction | 3 | 2 | 1 | 1 | 66.7% | 66.7% | 0.667 |
| android_specific_bugs | 3 | 3 | 3 | 0 | 50.0% | 100.0% | 0.667 |
| support_responsiveness | 2 | 1 | 3 | 1 | 25.0% | 50.0% | 0.333 |
| battery_life | 2 | 2 | 0 | 0 | 100.0% | 100.0% | 1.000 |
| android_feature_gaps | 2 | 2 | 3 | 0 | 40.0% | 100.0% | 0.571 |
| upsell_pressure | 2 | 2 | 1 | 0 | 66.7% | 100.0% | 0.800 |
| missing_language_support | 2 | 2 | 1 | 0 | 66.7% | 100.0% | 0.800 |
| redesign_regression | 2 | 2 | 19 | 0 | 9.5% | 100.0% | 0.174 |
| ai_autonomy | 1 | 1 | 0 | 0 | 100.0% | 100.0% | 1.000 |
| ai_only_support_channel | 1 | 1 | 1 | 0 | 50.0% | 100.0% | 0.667 |
| device_rendering_bugs | 1 | 1 | 0 | 0 | 100.0% | 100.0% | 1.000 |
| sleep_alarm_ui | 1 | 1 | 3 | 0 | 25.0% | 100.0% | 0.400 |
| third_party_integration | 1 | 1 | 3 | 0 | 25.0% | 100.0% | 0.400 |
| notification_community_issues | 1 | 0 | 1 | 1 | 0.0% | 0.0% | 0.000 |
| english_jargon_complexity | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| ecg_bp_feature_reliability | 0 | 0 | 2 | 0 | 0.0% | n/a | 0.000 |
| cardiac_detection_trust | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| strap_clasp_durability | 0 | 0 | 4 | 0 | 0.0% | n/a | 0.000 |

## Per-parent-category precision / recall / F1

| Parent category | Support | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| data_accuracy | 44 | 23 | 0 | 21 | 100.0% | 52.3% | 0.687 |
| ui_ux | 34 | 22 | 10 | 12 | 68.8% | 64.7% | 0.667 |
| sync_connectivity | 33 | 30 | 4 | 3 | 88.2% | 90.9% | 0.896 |
| pricing_billing | 32 | 32 | 7 | 0 | 82.1% | 100.0% | 0.901 |
| app_stability | 20 | 15 | 7 | 5 | 68.2% | 75.0% | 0.714 |
| sleep_tracking | 20 | 18 | 7 | 2 | 72.0% | 90.0% | 0.800 |
| customer_support | 17 | 15 | 2 | 2 | 88.2% | 88.2% | 0.882 |
| feature_requests | 16 | 15 | 15 | 1 | 50.0% | 93.8% | 0.652 |
| ai_coach | 11 | 10 | 2 | 1 | 83.3% | 90.9% | 0.870 |
| hardware_wearability | 10 | 9 | 8 | 1 | 52.9% | 90.0% | 0.667 |
| platform_parity | 5 | 5 | 6 | 0 | 45.5% | 100.0% | 0.625 |
| localization | 2 | 2 | 1 | 0 | 66.7% | 100.0% | 0.800 |
| health_signal_reliability | 0 | 0 | 2 | 0 | 0.0% | n/a | 0.000 |

## Borderline-pair confusion analysis

For each pair from `taxonomy_changelog.md`, a "swap" = the human tagged one side of the pair (and not the other), and the tagger predicted the other side instead (and not the first) — the exact failure mode the taxonomy fix was written to prevent. `both_correct` = review touches the pair and the tagger got the X/Y presence exactly right; `both_missed` = human tagged one of the pair, tagger predicted neither.

| Pair | Swapped X→Y | Swapped Y→X | Total swaps | Correctly resolved | Missed entirely |
|---|---|---|---|---|---|
| app_stability vs sync_connectivity | 0 | 0 | 0 | 14 | 2 |
| data_accuracy vs health_signal_reliability | 1 | 0 | 1 | 19 | 16 |
| sleep_tracking.sleep_alarm_ui vs ui_ux.redesign_regression | 0 | 0 | 0 | 3 | 0 |
| ui_ux.device_rendering_bugs vs platform_parity.android_specific_bugs | 0 | 0 | 0 | 4 | 0 |
| ai_coach.ai_autonomy vs customer_support.ai_only_support_channel | 0 | 0 | 0 | 2 | 0 |

## Watch categories — qualitative review

### ai_coach

13 eval review(s) touched by this category (human tag, predicted tag, or both).

- **[MISMATCH]** review_id `14299075270` [app_store, 3-star]
  - text: "I like the metrics and insights, but the AI has significant limitations. It creates problems it cannot undo. It logged strength training as indoor cycling. It logged indoor rowing as outdoor rowing. And it’s on me to report the bugs. This is beta tech at best."
  - human: activity_detection;metric_accuracy
  - predicted: activity_detection;ai_reliability_bugs
- **[MISMATCH]** review_id `14197690581` [app_store, 5-star]
  - text: "I’ve been using the WHOOP for almost a year now and it’s helped me to better manage my chronic illnesses and even helped me in managing my PTSD. I love the AI function where I can speak to it about any new concerns or changes and it always has an answer that’s backed up by research. It’s even helped"
  - human: ai_positive_reception;metric_accuracy
  - predicted: ai_positive_reception;personalization_use_case_fit;sleep_satisfaction
- **[MISMATCH]** review_id `13551987025` [app_store, 1-star]
  - text: "The app prioritizes trying to make me share “free trials” and then the shop and monetization. Kind of a bummer for something this expensive and personalized… just bad product leadership. 

I can’t seem to customize the home screen to see heart rate (seems like something core, over selling me stuff)…"
  - human: feature_ui_friction;personalization_use_case_fit;upsell_pressure
  - predicted: ai_reliability_bugs;missing_metrics;price_value_perception;upsell_pressure
- **[MISMATCH]** review_id `14182191121` [app_store, 4-star]
  - text: "Love that this keeps track of my data, and integrates with other things (like my scale). But the AI is terrible – prone to hallucinations that it claims are based on the data, but which aren’t."
  - human: ai_reliability_bugs
  - predicted: ai_reliability_bugs;third_party_integration
- **[MATCH]** review_id `b30ac348-0b58-49bb-a7a9-59ff6650e937` [google_play, 5-star]
  - text: "Insights, recommendations, and coaching are fantastic."
  - human: ai_positive_reception
  - predicted: ai_positive_reception
- **[MISMATCH]** review_id `13665043393` [app_store, 3-star]
  - text: "The app is okay. UI is odd. Would be better without the AI piece. Steps seem off— i.e. if you do something like an elliptical it doesn’t count it as “steps” (but will if you don’t log it as an activity)."
  - human: ai_autonomy;feature_ui_friction;metric_accuracy
  - predicted: ai_autonomy;metric_accuracy;missing_metrics
- **[MISMATCH]** review_id `13585882883` [app_store, 2-star]
  - text: "I enjoy using the WHOOP app, although some of the features  feel buried in odd places in the UI. but currently you can’t chat with WHOOP Coach without the app freezing!"
  - human: ai_reliability_bugs;feature_ui_friction
  - predicted: ai_reliability_bugs;redesign_regression
- **[MISMATCH]** review_id `14177657644` [app_store, 5-star]
  - text: "I’ve used whoop for about 6 years now and it’s changed my life. Knowing my metrics and being able to adjust to optimize my fitness shaped my journey post college sports. Not every day is a push day and whoop’s recovery features help me know when my body needs rest, so I don’t feel as if I’m just bei"
  - human: ai_positive_reception;metric_accuracy
  - predicted: ai_positive_reception;metric_accuracy;price_value_perception
- **[MISMATCH]** review_id `14307889928` [app_store, 5-star]
  - text: "Much more useful than some other options. The built in features allow tracking of so many different things (sleep, hydration, menstrual cycles, heart rate variability, sleep patterns, and more). The AI is great at analyzing & recommendations if that’s your thing. If I’m going to pay for one of these"
  - human: ai_positive_reception;metric_accuracy
  - predicted: ai_positive_reception
- **[MISMATCH]** review_id `218b9241-6d81-497b-a2aa-e3f65d79b758` [google_play, 5-star]
  - text: "The best health tracker on the market. Resilient, accurate and a lot of fun to use. Once you give it some time to know your lifestyle, it becomes a crucial part of your fitness life. Tracking metrics begins to give you strong insights of what you need to change, balance or improve upon in your every"
  - human: activity_detection;ai_positive_reception;metric_accuracy
  - predicted: ai_positive_reception
- **[MISMATCH]** review_id `14380724520` [app_store, 5-star]
  - text: "Whoop is not just a health monitor. The app analyzes your input response to help you make better choices for sleep, exercise, stress, and recovery.  It can forecast how you will be tomorrow based on your input about the level of strain you pushed yourself today, when you get to sleep, if you had a g"
  - human: ai_positive_reception
  - predicted: (none)
- **[MISMATCH]** review_id `14176328585` [app_store, 5-star]
  - text: "I really enjoy this app’s many features. Specifically my recovery and strain ranges. The Whoop AI Coach gives valuable advice as well. You can be very creative with your prompts and the coach gives a reliable answer around 80% of the time. The other 20% of the time the coach replies that the App can"
  - human: ai_reliability_bugs;metric_accuracy
  - predicted: ai_positive_reception;ai_reliability_bugs
- **[MATCH]** review_id `14330101752` [app_store, 2-star]
  - text: "Misses workouts, messes up sleep! The AI brain is the size of an acorn that’s been flattened by a 18 wheeler truck!"
  - human: activity_detection;ai_reliability_bugs;sleep_accuracy
  - predicted: activity_detection;ai_reliability_bugs;sleep_accuracy

### health_signal_reliability

2 eval review(s) touched by this category (human tag, predicted tag, or both).

- **[MISMATCH]** review_id `babf2f38-3962-48c4-be89-be64899fccf1` [google_play, 2-star]
  - text: "ekg not functional blood pressure not accurate sleep metrics accuracy is questionable"
  - human: metric_accuracy;sleep_accuracy
  - predicted: ecg_bp_feature_reliability;sleep_accuracy
- **[MISMATCH]** review_id `13766483189` [app_store, 4-star]
  - text: "You can’t swipe up to blood pressure insights on the health tab in the last two versions it just hangs. Fix it please."
  - human: crashes_freezes;feature_ui_friction
  - predicted: crashes_freezes;ecg_bp_feature_reliability

## Worst individual misses

Ranked by size of the symmetric difference between human and predicted tag sets (most disagreement first), tie-broken by lowest Jaccard.

### review_id `755de85d-9fb6-4dcd-b4d5-7944e9b25a03` [google_play, 3-star] — Jaccard 0.00

> This app is set towards young adults or those in their 20's, 30's and early 40's. It needs more activities for older people, for example church or synagogue service,visiting with friends, reading, for example for relaxing activities. The timer in which one flips for numbers is very difficult to use. Oxygen levels throughout the night would be helpful for those who need that information. The bpm levels while exercising should be divided into more categories in levels 1 and 2.

- **Human**: activity_detection
  - human notes: Primary fit: activity detection. Possible overlap with missing metrics; missing activity types.
- **Predicted**: feature_ui_friction;missing_activity_types;missing_metrics;personalization_use_case_fit

### review_id `13551987025` [app_store, 1-star] — Jaccard 0.17

> The app prioritizes trying to make me share “free trials” and then the shop and monetization. Kind of a bummer for something this expensive and personalized… just bad product leadership. 

I can’t seem to customize the home screen to see heart rate (seems like something core, over selling me stuff)… despite the ai engine continuing to tell me there are pencils or customization buttons that actually aren’t there in my version. Again, just seems like bad product management. Our family are not loving it thru day 1.

- **Human**: feature_ui_friction;personalization_use_case_fit;upsell_pressure
  - human notes: Core complaint spans upsell pressure, feature ui friction, and personalization use case fit; capped at three to keep the ground truth conservative.
- **Predicted**: ai_reliability_bugs;missing_metrics;price_value_perception;upsell_pressure

### review_id `13544073553` [app_store, 4-star] — Jaccard 0.00

> This thing rocks! The “Strength Trainer” function in the app needs to be further developed though. It’s clunky and you can’t see performance on past lifts while in a workout, which seems like an obvious feature to include.

- **Human**: activity_detection;missing_activity_types
  - human notes: Core complaint spans activity detection and missing activity types; kept both because they read as separate but related issues.
- **Predicted**: feature_ui_friction;missing_metrics

### review_id `f68f0dc2-a0e4-4a58-aae2-c32f84262448` [google_play, 4-star] — Jaccard 0.20

> I appreciate the concept of this product. However, the price point seems a bit high. Personally, I've found mine helpful for my weight loss journey. However, some aspects can be overly complex and overwhelming. I've been using this for over a month and feel there's still a lot to learn, especially considering the various add-ons. Some aspects that could improve the value proposition given the cost include simplifying data, addressing glitches and bugs, needs tutorial and enhancing integration.

- **Human**: feature_ui_friction;price_value_perception
  - human notes: Primary fit: price value perception, also user wants it to be simpler in terms of UI navigation and tutorials to actually educate or help them out.
- **Predicted**: crashes_freezes;personalization_use_case_fit;price_value_perception;third_party_integration

### review_id `0166af36-8098-40a7-aea6-62fd26c9b4b1` [google_play, 1-star] — Jaccard 0.33

> do not purchase or use ! this app is a criminal rort that will take your $ and not deliver on what it advertises app is difficult to navigate, device doesn't read correctly/acuretly, customer service is virtually non existent and you find yourself tlking to an AI bot that takes up more time than its worth !

- **Human**: ai_only_support_channel;feature_ui_friction;metric_accuracy;price_value_perception
  - human notes: Review raises four independent issues: poor value for money, difficult app navigation, inaccurate device readings, and frustration that support is effectively AI-only with no meaningful human assistance.
- **Predicted**: ai_only_support_channel;billing_disputes;metric_accuracy;redesign_regression

### review_id `b2d2edbc-2799-4a0c-b7f8-2cf87f77e5ae` [google_play, 2-star] — Jaccard 0.00

> New data screens and interface that display after sleep is confusing and difficult to understand compared to the simpler one prior to the update

- **Human**: feature_ui_friction
  - human notes: Primary fit: feature ui friction. Possible overlap with redesign regression.
- **Predicted**: redesign_regression;sleep_alarm_ui

### review_id `368412ca-6dac-48d5-a998-5c3ce88c7c9e` [google_play, 1-star] — Jaccard 0.00

> Great data. Whoop 3 outshines the Whoop 4. New app home screen is horribly cluttered.

- **Human**: feature_ui_friction
  - human notes: Primary fit: feature ui friction.
- **Predicted**: build_quality_perception;redesign_regression

### review_id `3f594dae-ede0-4adc-a9f3-123875f8fadc` [google_play, 3-star] — Jaccard 0.00

> I've updated my OnePlus 6T to Android 10 yesterday and today Whoop app says that my Bluetooth is disabled therefore is hasn't synced any data of the last 10 hours. Surely Bluetooth is enabled but for some reason the app doesn't see that. Please update your app so that I works with the latest Android OS.

- **Human**: update_failures
  - human notes: Primary fit: update failures.
- **Predicted**: android_specific_bugs;data_sync_delays

### review_id `cc3c34bb-2505-41fa-a7a8-33391bdad79b` [google_play, 5-star] — Jaccard 0.00

> Awesome app provides excellent health metrics and sleep data seems very accurate to me. Highly recommended!

- **Human**: metric_accuracy;sleep_accuracy
  - human notes: Primary fit: metric accuracy. Possible overlap with sleep satisfaction; sleep alarm ui.
- **Predicted**: sleep_satisfaction

### review_id `14233682537` [app_store, 3-star] — Jaccard 0.00

> Between Msgs to go to sleep by 9 pm, and no matter what I do, my recovery never gets above 60% even though I wake rested and feel great.

- **Human**: metric_accuracy
  - human notes: Primary fit: metric accuracy.
- **Predicted**: personalization_use_case_fit;sleep_accuracy

### review_id `14294280857` [app_store, 4-star] — Jaccard 0.00

> One suggestion I’d love to see is a Sleep-Friendly mode for the sensor light. The current flashing and pulsing light can be very bright and, on some nights, actually creates anxiety and makes it difficult to fall asleep. It’s especially ironic since the app provides guidance on avoiding bright light before bed to support better sleep. A dim, steady, or optional light setting would make the experience much more sleep-friendly while still serving its purpose.

- **Human**: sleep_satisfaction
  - human notes: Primary fit: sleep satisfaction.
- **Predicted**: missing_activity_types;personalization_use_case_fit

### review_id `33d4176f-d357-4007-ad12-0feca8dedc69` [google_play, 5-star] — Jaccard 0.00

> I bought it to watch my strain/recovery, as I train many hours most days. So far really happy, even though I was always quite mindful of sleep, it makes me more vigilant, not just with sleep, but more so with restorative activities, as I want to try and be in green recivery as much as possible.

- **Human**: activity_detection;metric_accuracy
  - human notes: Core complaint spans activity detection and metric accuracy; kept both because they read as separate but related issues.
- **Predicted**: sleep_satisfaction

### review_id `13494529245` [app_store, 1-star] — Jaccard 0.00

> I mean I am absolutely put off by how I can use the app. Why am I not able to see day view for heart rate, sleep etc. I do not understand how to use it, I am returning it. I am really sorry, there is a long way yo go

- **Human**: feature_ui_friction
  - human notes: Reviewer finds the app difficult to understand and navigate, specifically struggling to locate day views for heart rate and sleep. Complaint centers on usability and discoverability rather than missing functionality or inaccurate data.
- **Predicted**: redesign_regression;sleep_alarm_ui

### review_id `1f963d47-b263-4b82-a9a4-83b9161b9bbd` [google_play, 3-star] — Jaccard 0.00

> Good app but still bugs in it. App won't request permission to view files so " Select from Gallery" doesn't work. Also it would be great if there was an on screen widget or overlay so when watching nextflix or a podcast you could track HR

- **Human**: feature_ui_friction
  - human notes: Primary fit: feature ui friction.
- **Predicted**: crashes_freezes;missing_metrics

### review_id `d063a147-6a35-4c75-a10e-a5500eeee655` [google_play, 2-star] — Jaccard 0.00

> Interesting device, but it's too complicated to manage. There are too many settings to get something useful. It should have simple defaults unless someone wants more insights

- **Human**: feature_ui_friction
  - human notes: Reviewer finds the app overly complex and believes it should provide simpler default settings with advanced options available only when desired. Complaint centers on usability and workflow complexity rather than missing functionality.
- **Predicted**: personalization_use_case_fit;redesign_regression
