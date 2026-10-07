"""Semantic search over WHOOP reviews -- finds reviews by meaning, not just
exact keyword match (e.g. "battery drain" also surfaces "dies overnight").
All embeddings are normalized at encode time (see embeddings.py), so cosine
similarity is a plain dot product.

CLI (from backend/, needs requirements-semantic.txt installed):
  python -m semantic.search "battery draining overnight" --top-k 10
"""

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd

from semantic.embeddings import embed_query, get_embeddings

DATA_DIR = __import__("pathlib").Path(__file__).parent.parent / "data"
TAGGED_PATH = DATA_DIR / "tagged_reviews.csv"


def semantic_search(query: str, df: pd.DataFrame, embeddings: dict[str, np.ndarray], top_k: int = 10) -> list[dict]:
    """Returns up to top_k reviews most similar to query, each a real row
    from df -- no generated/paraphrased text, just real reviews ranked."""
    q_vec = embed_query(query)
    ids = list(embeddings.keys())
    if not ids:
        return []
    matrix = np.stack([embeddings[i] for i in ids])
    scores = matrix @ q_vec

    order = np.argsort(-scores)[:top_k]
    by_id = df.set_index(df["review_id"].astype(str))
    results = []
    for idx in order:
        rid = ids[idx]
        if rid not in by_id.index:
            continue
        row = by_id.loc[rid]
        results.append({
            "review_id": rid,
            "score": float(scores[idx]),
            "text": row["text"],
            "source": row["source"],
            "rating": int(row["rating"]) if not pd.isna(row["rating"]) else None,
            "date": row["date"],
        })
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    df = pd.read_csv(TAGGED_PATH)
    df = df[df["status"] == "OK"]
    embeddings = get_embeddings(df)
    results = semantic_search(args.query, df, embeddings, top_k=args.top_k)

    print(f"\nTop {len(results)} result(s) for: {args.query!r}\n")
    for r in results:
        print(f"[{r['score']:.3f}] {r['source']} {r['rating']}★ {r['date']}")
        print(f"  {r['text'][:200]}")
        print()


if __name__ == "__main__":
    main()
