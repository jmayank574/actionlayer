"""Maps the shorthand codes used in data/open_coding.csv (e.g. "PB.value")
to the real subcategory ids in data/taxonomy.yaml (e.g. "price_value_perception").

open_coding.csv predates taxonomy.yaml's final id naming — it was written
during open coding using short internal codes for speed. This mapping is the
single place that translates between the two, used when curating few-shot
examples for the tagger prompt.
"""

SHORTHAND_TO_SUBCATEGORY_ID = {
    "PB.value": "price_value_perception",
    "PB.billing": "billing_disputes",
    "PB.plan": "plan_trial_structure",
    "PB.upsell": "upsell_pressure",
    "ST.accuracy": "sleep_accuracy",
    "ST.satisfaction": "sleep_satisfaction",
    "ST.ui": "sleep_alarm_ui",
    "HW.strap": "strap_clasp_durability",
    "HW.comfort": "comfort_fit",
    "HW.battery": "battery_life",
    "HW.quality": "build_quality_perception",
    "SY.onboarding": "onboarding_pairing",
    "SY.disconnect": "ongoing_disconnects",
    "SY.datasync": "data_sync_delays",
    "DA.accuracy": "metric_accuracy",
    "DA.activitydetect": "activity_detection",
    "HS.cardiac": "cardiac_detection_trust",
    "HS.ecgbp": "ecg_bp_feature_reliability",
    "AI.bugs": "ai_reliability_bugs",
    "AI.autonomy": "ai_autonomy",
    "AI.positive": "ai_positive_reception",
    "CS.responsive": "support_responsiveness",
    "CS.resolution": "support_resolution_quality",
    "CS.ai_only_support_channel": "ai_only_support_channel",
    "CS.positive": "support_satisfaction",
    "AS.crash": "crashes_freezes",
    "AS.update": "update_failures",
    "UX.redesign": "redesign_regression",
    "UX.device": "device_rendering_bugs",
    "UX.feature": "feature_ui_friction",
    "UX.notif": "notification_community_issues",
    "PP.gaps": "android_feature_gaps",
    "PP.bugs": "android_specific_bugs",
    "LOC.missing": "missing_language_support",
    "LOC.jargon": "english_jargon_complexity",
    "FR.activity": "missing_activity_types",
    "FR.metrics": "missing_metrics",
    "FR.personalization": "personalization_use_case_fit",
    "FR.integration": "third_party_integration",
}


def convert_tags(shorthand_tags: list[str]) -> list[str]:
    """Convert a list of open_coding.csv shorthand codes to real subcategory ids.
    Raises KeyError on an unmapped code so a mapping gap fails loudly."""
    return [SHORTHAND_TO_SUBCATEGORY_ID[t] for t in shorthand_tags]
