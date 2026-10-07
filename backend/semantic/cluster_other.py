"""Clusters the "Other/Ungrouped" reviews (the ~20% the tagger couldn't fit
into any existing taxonomy subcategory) into groups, and asks Claude to
propose a name + definition for each group from real representative reviews.

Deterministic clustering (KMeans over local embeddings) decides the groups;
Claude only names and describes groups it's shown -- same explain-don't-decide
split as ops/health_check.py and ops/ui_qa_diagnose.py. This never edits
taxonomy.yaml. It writes a proposal document for a human to review and, if
they agree, turn into an actual taxonomy change by hand (or a future PR) --
see the roadmap rule in PROGRESS.md: "it proposes via PR/issue, you approve."

Run with (from backend/, needs requirements-semantic.txt installed):
  python -m semantic.cluster_other              uses a default k
  python -m semantic.cluster_other --k 8
"""

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

from semantic.embeddings import get_embeddings

DATA_DIR = Path(__file__).parent.parent / "data"
TAGGED_PATH = DATA_DIR / "tagged_reviews.csv"
OUT_MD = DATA_DIR / "other_cluster_proposals.md"
OUT_JSON = DATA_DIR / "other_cluster_proposals.json"
EXAMPLES_PER_CLUSTER = 6


def load_other_bucket() -> pd.DataFrame:
    df = pd.read_csv(TAGGED_PATH)
    df = df[df["status"] == "OK"]
    other = df[df["subcategory_tags"].isna() | (df["subcategory_tags"] == "")]
    return other


def run_clustering(other: pd.DataFrame, embeddings: dict[str, np.ndarray], k: int) -> dict[int, list[str]]:
    """Returns {cluster_id: [review_id, ...]} -- plain KMeans, no AI."""
    from sklearn.cluster import KMeans

    ids = [rid for rid in other["review_id"].astype(str) if rid in embeddings]
    matrix = np.stack([embeddings[rid] for rid in ids])

    km = KMeans(n_clusters=k, n_init=10, random_state=0)
    labels = km.fit_predict(matrix)

    clusters: dict[int, list[str]] = {}
    for rid, label, vec in zip(ids, labels, matrix):
        clusters.setdefault(int(label), []).append(rid)

    # Order each cluster's members by closeness to its own centroid so the
    # representative examples shown to Claude are the most "typical" members,
    # not arbitrary ones.
    ordered: dict[int, list[str]] = {}
    for label, members in clusters.items():
        centroid = km.cluster_centers_[label]
        member_vecs = {rid: embeddings[rid] for rid in members}
        ranked = sorted(members, key=lambda rid: -float(member_vecs[rid] @ centroid))
        ordered[label] = ranked
    return ordered


def propose_names(clusters: dict[int, list[str]], other: pd.DataFrame) -> list[dict]:
    """One Claude call describing all clusters at once (cheaper than one call
    per cluster). Claude proposes a name/definition per cluster from the real
    example reviews it's shown -- it does not decide cluster membership."""
    from evals.preflight import api_error
    problem = api_error()
    if problem:
        raise RuntimeError(f"API not usable: {problem}")

    from anthropic import Anthropic
    client = Anthropic()

    by_id = other.set_index(other["review_id"].astype(str))
    cluster_blocks = []
    for label, members in sorted(clusters.items()):
        examples = members[:EXAMPLES_PER_CLUSTER]
        texts = [by_id.loc[rid, "text"] for rid in examples if rid in by_id.index]
        block = f"Cluster {label} ({len(members)} reviews, showing {len(texts)} representative examples):\n"
        block += "\n".join(f"- {t[:300]}" for t in texts)
        cluster_blocks.append(block)

    prompt = (
        "These are clusters of WHOOP app reviews that an existing taxonomy-based tagger could not "
        "fit into any current category (the 'Other/Ungrouped' bucket). Each cluster below was formed "
        "by unsupervised clustering of review-text embeddings, not by you -- your only job is to look "
        "at the real example reviews in each cluster and propose, for each one, a short candidate "
        "subcategory name and a one-sentence definition, in the same style as this project's taxonomy "
        "(e.g. 'Price / Value Perception: Judgment that the subscription costs too much for what it "
        "delivers.'). If a cluster is incoherent or too mixed to name meaningfully, say so honestly "
        "instead of forcing a name.\n\n"
        "Respond with ONLY a JSON array, one object per cluster, no markdown fencing:\n"
        '[{"cluster_id": 0, "proposed_name": "...", "definition": "...", "coherent": true}]\n\n'
        + "\n\n".join(cluster_blocks)
    )

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def build_report(proposals: list[dict], clusters: dict[int, list[str]], other: pd.DataFrame, total_corpus: int) -> str:
    by_id = other.set_index(other["review_id"].astype(str))
    lines = [
        "# Other/Ungrouped cluster proposals",
        "",
        f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
        f"{len(other)} reviews ({len(other) / total_corpus:.1%} of the tagged corpus) are "
        "currently Other/Ungrouped, clustered into the groups below.",
        "",
        "**This is a proposal, not a taxonomy change.** Nothing in `taxonomy.yaml` is edited by this "
        "script. Review each cluster below; if a proposed subcategory looks real, add it to "
        "`taxonomy.yaml` by hand (or via a reviewed PR) and run `tag_reviews.py --full` to apply it.",
        "",
    ]
    by_cluster_id = {p["cluster_id"]: p for p in proposals}
    for label, members in sorted(clusters.items()):
        p = by_cluster_id.get(label, {})
        name = p.get("proposed_name", "(no proposal)")
        definition = p.get("definition", "")
        coherent = p.get("coherent", True)
        pct = len(members) / len(other) * 100
        lines.append(f"## Cluster {label}: {name}{'' if coherent else ' (flagged as incoherent)'}")
        lines.append(f"{len(members)} reviews ({pct:.1f}% of Other/Ungrouped)")
        lines.append("")
        if definition:
            lines.append(f"> {definition}")
            lines.append("")
        lines.append("Example reviews:")
        for rid in members[:EXAMPLES_PER_CLUSTER]:
            if rid in by_id.index:
                text = by_id.loc[rid, "text"]
                lines.append(f"- *(review {rid})* {text[:220]}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=None, help="number of clusters (default: scaled to bucket size)")
    args = parser.parse_args()

    other = load_other_bucket()
    all_tagged = pd.read_csv(TAGGED_PATH)
    all_tagged = all_tagged[all_tagged["status"] == "OK"]
    print(f"{len(other)} reviews in Other/Ungrouped out of {len(all_tagged)} tagged ({len(other) / len(all_tagged):.1%}).")

    k = args.k or max(4, min(12, len(other) // 60))
    print(f"Clustering into k={k} groups...")

    embeddings = get_embeddings(other)
    clusters = run_clustering(other, embeddings, k)

    print("Asking Claude to propose a name for each cluster...")
    proposals = propose_names(clusters, other)

    report = build_report(proposals, clusters, other, len(all_tagged))
    OUT_MD.write_text(report, encoding="utf-8")
    OUT_JSON.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "other_bucket_size": len(other),
        "total_corpus": len(all_tagged),
        "k": k,
        "clusters": {str(label): members for label, members in clusters.items()},
        "proposals": proposals,
    }, indent=2), encoding="utf-8")

    print(f"\nWrote {OUT_MD} and {OUT_JSON}")
    print(report)


if __name__ == "__main__":
    main()
