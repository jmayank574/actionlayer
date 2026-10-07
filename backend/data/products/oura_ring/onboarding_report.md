# Onboarding draft: Oura Ring

**Nothing here is live.** No file in `backend/data/` outside `products/oura_ring/` was touched, and `tag_reviews.py` was not run. This is a draft for a human to review -- see the roadmap rule: agents propose via PR/issue, you approve.

- Ingested: 8706 real reviews
- Open-coding sample: 60 reviews
- Draft taxonomy: 10 parent categories, 33 subcategories
- Eval seed: 40 reviews set aside, unlabeled, for hand-labeling

## Draft taxonomy

### Data & Measurement Accuracy (`data_accuracy`)
Reviews questioning whether the ring's sensor readings and calculated metrics reflect reality.
- **Sleep Tracking Accuracy** (`sleep_tracking_accuracy`) -- Complaints or praise about how accurately the ring detects sleep onset, duration, and stages. _(sample ids: [1, 11, 21, 28, 48, 51])_
- **Activity & Step Detection Accuracy** (`activity_detection_accuracy`) -- Feedback about the ring misidentifying, over-detecting, or under-detecting physical activities and step counts. _(sample ids: [4, 29, 35, 43, 59])_
- **Calorie Tracking Accuracy** (`calorie_tracking_accuracy`) -- Concerns that calorie burn estimates are incorrect or changed negatively after an update. _(sample ids: [16, 57])_
- **General Metric Inaccuracy** (`general_metric_inaccuracy`) -- Broad claims that multiple metrics or overall data quality have become unreliable over time. _(sample ids: [20, 36])_

### App Stability & Performance (`app_stability_performance`)
Reviews focused on technical bugs, crashes, freezes, slow syncing, or the app failing to open.
- **App Crashes & Freezes** (`app_crashes_freezes`) -- Reports of the app crashing, going black, or becoming completely unusable. _(sample ids: [18, 39, 47])_
- **Sync & Bluetooth Connectivity Issues** (`sync_connectivity_issues`) -- Difficulty getting the ring to maintain a Bluetooth connection or push data to the app. _(sample ids: [5, 9, 14, 52])_
- **App Update Problems** (`app_update_problems`) -- Issues triggered by or caused during the app update process itself. _(sample ids: [17, 44, 46])_
- **UI Bugs & Display Errors** (`ui_navigation_bugs`) -- Visual glitches such as the home screen refreshing constantly, wrong dates shown, or persistent intrusive banners. _(sample ids: [16, 17, 44])_

### Battery Life & Degradation (`battery_life`)
Reviews about how long the ring holds a charge, including degradation over time.
- **Battery Degradation Over Time** (`battery_degradation_over_time`) -- Users reporting that battery life declined significantly after several months of use. _(sample ids: [38, 45, 56, 60])_
- **Battery Life Praise** (`battery_life_positive`) -- Users expressing satisfaction with how long the ring lasts on a single charge. _(sample ids: [8, 24])_
- **Battery Life Concerns** (`battery_life_concerns`) -- Users unsatisfied with current battery duration without attributing it to degradation specifically. _(sample ids: [23])_

### Hardware Durability & Reliability (`hardware_durability_reliability`)
Reviews about the physical ring breaking, failing, or becoming non-functional.
- **Ring Failure & Short Lifespan** (`ring_failure_short_lifespan`) -- Reports of the ring stopping all function or tracking within months of purchase. _(sample ids: [19, 30, 12])_
- **Perceived Planned Obsolescence** (`deliberate_obsolescence`) -- Suspicion that older rings are intentionally degraded or de-supported when new hardware is released. _(sample ids: [13])_
- **Physical Form Factor Feedback** (`physical_form_factor_feedback`) -- Comments about the ring's size, thickness, or wearability on different hand sizes. _(sample ids: [8])_

### Customer Support Experience (`customer_support`)
Reviews describing interactions with Oura's support team, warranty process, or AI bot.
- **Slow or No Response from Support** (`slow_or_no_response`) -- Users reporting that support tickets go unanswered for weeks or months. _(sample ids: [3, 36])_
- **Warranty Claim Difficulties** (`warranty_claim_difficulties`) -- Frustration with a lengthy, complicated, or unsuccessful hardware warranty or replacement process. _(sample ids: [30])_
- **AI Chatbot Deflection** (`ai_bot_deflection`) -- Complaints that support routes users to an AI bot rather than a human agent who can resolve issues. _(sample ids: [23])_

### Subscription, Data Privacy & Trust (`subscription_data_privacy`)
Reviews about the subscription model, handling of personal health data, and user trust.
- **Data Privacy & Third-Party Data Concerns** (`data_privacy_concerns`) -- Users uneasy about Oura sharing or mishandling sensitive health data with third-party services. _(sample ids: [7, 20, 55])_
- **Value for Money** (`value_for_money`) -- Opinions on whether the ring and subscription cost are justified by the benefits received. _(sample ids: [18, 30])_

### App UX & Design (`app_ux_design`)
Feedback on the user interface design, navigation, and overall usability of the app.
- **UI Redesign Regression** (`ui_redesign_regression`) -- Users preferring an older UI version and finding the newer design harder to use or requiring more clicks. _(sample ids: [27, 41])_
- **Missing Features & Customization Gaps** (`missing_features_customization`) -- Requests for features that are absent, such as saving custom activity names or dismissing notifications. _(sample ids: [15, 50, 54])_
- **Generic or Repetitive AI Insights** (`preprogrammed_generic_insights`) -- Criticism that readiness and sleep score commentary feels scripted, repetitive, and unhelpful. _(sample ids: [4, 42])_
- **Platform Feature Parity** (`platform_feature_parity`) -- Frustration that certain features available on one platform (e.g., iOS) are not yet on another (e.g., Android). _(sample ids: [22])_
- **Intrusive In-App Notifications** (`intrusive_notifications`) -- Annoyance at persistent banners or prompts that cannot be dismissed and obstruct normal app use. _(sample ids: [32, 44])_

### Health Insights & Personal Value (`health_insights_value`)
Reviews describing positive impact on health decisions, sleep improvement, or early health detection.
- **Sleep Improvement Impact** (`sleep_improvement_impact`) -- Users crediting Oura data with meaningfully improving their sleep quality or habits. _(sample ids: [21, 25, 33, 40])_
- **Early Health Detection** (`early_health_detection`) -- Reports of the ring flagging unexpected health events such as pregnancy or illness before the user was aware. _(sample ids: [10])_
- **Holistic Health & Wellness Optimization** (`holistic_health_optimization`) -- Broad praise for the ring helping users optimize workouts, stress management, and overall wellness. _(sample ids: [26, 31, 34, 53, 58])_
- **Stress & Readiness Tracking Utility** (`stress_tracking_utility`) -- Feedback specifically about the stress score or readiness metric being useful or causing anxiety. _(sample ids: [49])_
- **Menstrual Cycle & Temperature Tracking** (`menstrual_cycle_tracking`) -- Positive feedback about using basal body temperature trends for cycle tracking. _(sample ids: [35])_

### Third-Party & Ecosystem Integration (`third_party_integration`)
Requests or feedback about connecting Oura data with other health platforms or devices.
- **Health Platform Integration Requests** (`health_platform_integration`) -- Users wanting better or new integrations with platforms such as Apple Health or Google Health Connect. _(sample ids: [37])_
- **Third-Party Device Integration Requests** (`device_integration_requests`) -- Requests to import or sync data from other health devices such as continuous glucose monitors or blood pressure cuffs. _(sample ids: [37])_

### Ungrouped / Other (`ungrouped`)
Reviews that did not fit any coherent recurring theme identified in this sample.
- **Ideological or Policy Complaint** (`ideological_complaint`) -- A review objecting to a specific company policy or terminology choice unrelated to product function. _(sample ids: [2])_
- **Specific Feature Alert Request** (`feature_alert_request`) -- A one-off request for a specific new notification feature not echoed elsewhere in the sample. _(sample ids: [6])_

## Next steps for a human reviewer

1. Read `products/oura_ring/taxonomy_draft.yaml` against the sample reviews it cites.
2. Edit/merge it into a real taxonomy.yaml for this product once it looks right.
3. Hand-label `products/oura_ring/eval_seed.csv` (fill in parent_category_tags/subcategory_tags) so there's an eval gate before tagging the full corpus, same as WHOOP's evals/tagger_eval.py.
4. Only then run tagging on this product's full dataset.