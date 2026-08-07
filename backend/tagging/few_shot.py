"""Curates few-shot examples for the tagging prompt from data/open_coding.csv
(the 180 reviews used to BUILD the taxonomy). Never touches data/eval_sample.csv.

Prioritizes the 5 borderline pairs documented in taxonomy_changelog.md  -  those
are exactly where a naive tagger is most likely to fail  -  then fills in general
coverage across the remaining parent categories, a couple of Other/Ungrouped
examples, and a couple of clearly multi-label examples.
"""

from pathlib import Path

import pandas as pd

from tagging.code_mapping import convert_tags

DATA_DIR = Path(__file__).parent.parent / "data"

# sample_id -> short note on why this pair matters. Hand-picked because these
# specific reviews best demonstrate each boundary (including one review, 34,
# that spans both sides of the AI Coach / support-channel split  -  exactly the
# case the v1->v2 taxonomy fix was written for).
BORDERLINE_PICKS = {
    89: "app_stability vs sync_connectivity  -  this is a crash/instability complaint (activities disappear, app malfunctions), not a data-sync complaint, even though both can look like 'the app doesn't work.'",
    17: "app_stability vs sync_connectivity  -  this is a data-availability complaint (app requires connectivity to show already-collected data) tagged under sync, not a crash.",
    82: "data_accuracy vs health_signal_reliability  -  this is a generic HR-during-exercise accuracy complaint (metric_accuracy), no diagnosed condition or ECG/BP feature involved, so it stays in data_accuracy even though it's about heart rate.",
    56: "data_accuracy vs health_signal_reliability  -  this review names a diagnosed cardiac condition and the device failing to detect known episodes; that specific clinical framing is what moves it into health_signal_reliability instead of generic accuracy.",
    170: "sleep_tracking.sleep_alarm_ui vs ui_ux.redesign_regression  -  the complaint is specifically about finding the alarm after a redesign, so sleep_alarm_ui is primary even though a redesign caused it.",
    101: "sleep_tracking.sleep_alarm_ui vs ui_ux.redesign_regression  -  this redesign complaint is about general navigation/data density, not sleep or the alarm specifically, so it's redesign_regression only.",
    98: "ui_ux.device_rendering_bugs vs platform_parity.android_specific_bugs  -  this is a form-factor/screen-size rendering bug (foldable phone) on an Android device, but the complaint isn't about Android losing out to iOS, so it's device_rendering_bugs, not android_specific_bugs.",
    109: "ui_ux.device_rendering_bugs vs platform_parity.android_specific_bugs  -  this explicitly frames Android as getting a worse experience than iOS (needed an iPhone to complete setup), which is what makes it android_specific_bugs.",
    34: "ai_coach.ai_autonomy vs customer_support.ai_only_support_channel  -  this single review contains BOTH shapes: 'can't disable the AI coach' (ai_autonomy) and 'customer support is entirely AI, no human' (ai_only_support_channel)  -  tag both, don't collapse them into one.",
    77: "ai_coach.ai_autonomy vs customer_support.ai_only_support_channel  -  this is the support-channel shape only (AI support, no way to reach a human); there's no AI Coach feature-control complaint here, so ai_autonomy does NOT apply.",
}

RANDOM_SEED = 7
N_GENERAL_COVERAGE = 10
N_OTHER_EXAMPLES = 2
N_MULTI_LABEL_EXTRA = 3


def _load_joined() -> pd.DataFrame:
    sample = pd.read_csv(DATA_DIR / "taxonomy_sample.csv")
    coding = pd.read_csv(DATA_DIR / "open_coding.csv")
    return sample.merge(coding[["sample_id", "tags", "tag_count"]], on="sample_id")


def build_few_shot_examples() -> list[dict]:
    df = _load_joined()

    chosen_ids: list[int] = list(BORDERLINE_PICKS.keys())

    # General coverage: fill in parent categories not already represented,
    # preferring single-tag rows so the example is unambiguous.
    already = set(chosen_ids)
    covered_subcats: set[str] = set()
    for sid in chosen_ids:
        row = df[df["sample_id"] == sid].iloc[0]
        if row["tags"] != "OTHER_UNGROUPED":
            covered_subcats.update(convert_tags(row["tags"].split(";")))

    single_tag_rows = df[(df["tag_count"] == 1) & (~df["sample_id"].isin(already))]
    candidates = single_tag_rows.sample(frac=1, random_state=RANDOM_SEED)
    for _, row in candidates.iterrows():
        subcats = convert_tags(row["tags"].split(";"))
        if not any(s in covered_subcats for s in subcats):
            chosen_ids.append(int(row["sample_id"]))
            covered_subcats.update(subcats)
            already.add(row["sample_id"])
        if len(chosen_ids) - len(BORDERLINE_PICKS) >= N_GENERAL_COVERAGE:
            break

    # A couple of Other/Ungrouped examples, so zero-tag output is modeled explicitly.
    other_rows = df[(df["tags"] == "OTHER_UNGROUPED") & (~df["sample_id"].isin(already))]
    other_picks = other_rows.sample(n=min(N_OTHER_EXAMPLES, len(other_rows)), random_state=RANDOM_SEED)
    chosen_ids.extend(int(x) for x in other_picks["sample_id"])
    already.update(other_picks["sample_id"])

    # A few more heavily multi-label examples (3+ tags), to reinforce that
    # multi-label is the norm, not an edge case.
    heavy_multi = df[(df["tag_count"] >= 3) & (~df["sample_id"].isin(already))]
    multi_picks = heavy_multi.sample(n=min(N_MULTI_LABEL_EXTRA, len(heavy_multi)), random_state=RANDOM_SEED)
    chosen_ids.extend(int(x) for x in multi_picks["sample_id"])

    examples = []
    for sid in chosen_ids:
        row = df[df["sample_id"] == sid].iloc[0]
        subcats = [] if row["tags"] == "OTHER_UNGROUPED" else convert_tags(row["tags"].split(";"))
        examples.append({
            "sample_id": sid,
            "source": row["source"],
            "rating": int(row["rating"]),
            "text": row["text"],
            "subcategory_ids": subcats,
            "note": BORDERLINE_PICKS.get(sid),
        })
    return examples


def render_few_shot_text(examples: list[dict], parent_lookup: dict[str, str]) -> str:
    lines = ["# Worked examples (real reviews, human-labeled during taxonomy construction)\n"]
    for i, ex in enumerate(examples, 1):
        lines.append(f"Example {i} [{ex['source']}, {ex['rating']}-star]:")
        lines.append(f'Review: "{ex["text"]}"')
        if ex["subcategory_ids"]:
            tag_strs = [f"{parent_lookup[s]} > {s}" for s in ex["subcategory_ids"]]
            lines.append("Correct tags: " + "; ".join(tag_strs))
        else:
            lines.append("Correct tags: (none  -  Other/Ungrouped. Do not force a tag here.)")
        if ex.get("note"):
            lines.append(f"Why: {ex['note']}")
        lines.append("")
    return "\n".join(lines)
