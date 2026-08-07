# Taxonomy v3 candidates — deferred gaps found during eval labeling

Not acted on now — taxonomy stayed locked through eval-set labeling so nothing here 
invalidates already-completed work. Revisit once Step 3 tags the full 3,295 reviews and 
real volume is known, same standard used to build v1/v2 (evidence first, category second).

## 1. Hardware aesthetics / industrial design
Currently folded into `build_quality_perception` or `comfort_fit`. Full-dataset keyword 
check found only ~2/3,295 reviews as genuine standalone aesthetic complaints (color fading, 
"looks ugly"), both bundled with comfort complaints in the same sentence. Likely stays 
folded in — check real tagged volume once Step 3 runs before deciding.

## 2. Confirmed hardware defect / DOA, distinct from build_quality_perception
Surfaced in eval labeling (eval_id 62): a genuinely defective/DOA sensor is a different 
claim than "feels cheap" (build_quality_perception is about *perception*, not a confirmed 
failure) and doesn't fit strap_clasp_durability (mechanical/clasp-specific). No dedicated 
subcategory currently. Worth checking if this is a recurring pattern at full-dataset scale.

## 3. iOS-specific bugs — platform_parity is currently Android-only
Surfaced in eval labeling (eval_id 119): a real iOS-specific interaction bug (exercise-log 
scrolling broken on iOS) had nowhere to go — `platform_parity`'s subcategories 
(`android_feature_gaps`, `android_specific_bugs`) only cover Android falling behind iOS, 
not the reverse. This asymmetry was a deliberate reflection of what the original 180-review 
taxonomy-design sample actually contained, not an oversight — but it means the taxonomy 
currently can't represent an iOS-specific bug at all. Tagged as ui_ux > feature_ui_friction 
only for this eval row, with platform_parity dropped rather than left unpaired. If Step 3 
surfaces a real cluster of iOS-specific complaints, add `ios_specific_bugs` as a sibling to 
the existing two Android subcategories.

## 4. ecg_bp_feature_reliability doesn't require a diagnosis, unlike cardiac_detection_trust
Surfaced during the health_signal_reliability prompt-tightening investigation (see 
data/tagging_pipeline_notes.md). Eval review babf2f38-3962-48c4-be89-be64899fccf1 ("ekg not 
functional blood pressure not accurate sleep metrics accuracy is questionable") was 
hand-labeled metric_accuracy;sleep_accuracy, but ecg_bp_feature_reliability's current written 
definition ("The ECG or blood-pressure-adjacent features are slow, unreliable, or 
burdensome") doesn't require a named diagnosis or clinical episode the way 
cardiac_detection_trust's does — read literally, this review qualifies either way. The 
tagger firing ecg_bp_feature_reliability here survived three separate prompt-fix attempts, 
none of which resolved it, which is itself evidence this is a taxonomy definition gap rather 
than a promptable tagger error. Worth tightening ecg_bp_feature_reliability's 
definition/excludes text to match cardiac_detection_trust's stricter bar once Step 3 volume 
shows how often this ambiguity actually recurs.
