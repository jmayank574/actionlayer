"""Loads and renders data/taxonomy.yaml for the tagging prompt.

The prompt needs the full definition/includes/excludes text for every
subcategory, not just names — that boundary text is what resolves the
borderline pairs documented in taxonomy_changelog.md (app_stability vs sync,
ai_autonomy vs ai_only_support_channel, etc).
"""

from pathlib import Path

import yaml

TAXONOMY_PATH = Path(__file__).parent.parent / "data" / "taxonomy.yaml"


def load_taxonomy() -> dict:
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def subcategory_to_parent_map(taxonomy: dict) -> dict[str, str]:
    """subcategory_id -> parent_id. Used so the parent field in tagging output
    is always derived from our own taxonomy, never trusted from model output."""
    mapping = {}
    for cat in taxonomy["categories"]:
        for sub in cat["subcategories"]:
            mapping[sub["id"]] = cat["id"]
    return mapping


def valid_subcategory_ids(taxonomy: dict) -> set[str]:
    return set(subcategory_to_parent_map(taxonomy).keys())


def watch_category_ids(taxonomy: dict) -> set[str]:
    return {cat["id"] for cat in taxonomy["categories"] if cat.get("watch_category")}


def render_taxonomy_text(taxonomy: dict) -> str:
    """Full category/subcategory text for the system prompt: definitions,
    paraphrased includes, and excludes/boundary notes for every subcategory."""
    lines = [f"# Taxonomy: {taxonomy['product']} (v{taxonomy['version']})\n"]
    for cat in taxonomy["categories"]:
        watch = "  [WATCH CATEGORY — low volume, high stakes; do not under-tag this even if unsure]" if cat.get("watch_category") else ""
        lines.append(f"## {cat['id']} — {cat['name']}{watch}")
        lines.append(cat["definition"].strip())
        if cat.get("watch_reason"):
            lines.append(f"Why this is a watch category: {cat['watch_reason'].strip()}")
        lines.append("")
        for sub in cat["subcategories"]:
            lines.append(f"### {sub['id']} — {sub['name']}")
            definition = sub["definition"]
            lines.append(f"Definition: {definition.strip() if isinstance(definition, str) else definition}")
            if sub.get("includes"):
                lines.append("Includes (examples of what belongs here):")
                for ex in sub["includes"]:
                    lines.append(f"  - {ex}")
            excludes = sub.get("excludes", "")
            if excludes and excludes.strip() and excludes.strip() != "(none notable)":
                lines.append(f"Excludes / boundary vs. nearest-neighbor categories: {excludes.strip()}")
            lines.append("")
    return "\n".join(lines)
