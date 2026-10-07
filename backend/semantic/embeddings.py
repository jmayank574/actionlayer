"""Review-text embeddings, cached and incremental -- same discipline as
tagging (backend/tagging/tagger.py): embedding the whole corpus on every run
would be pure waste once most reviews are already embedded. Unlike tagging,
this costs nothing per call (a local sentence-transformers model, no API),
so the only thing incrementality buys here is time, not money -- but the
corpus will keep growing daily, so it still matters.

Model: all-MiniLM-L6-v2 (384-dim, ~80MB, CPU-friendly). Picked over a paid
embeddings API (OpenAI/Voyage) specifically to avoid adding a second paid
credential to a pipeline that currently needs only ANTHROPIC_API_KEY -- see
CLAUDE.md's Environment Variables section. Good enough for nearest-neighbor
review search and clustering; not a claim of SOTA retrieval quality.

Needs backend/requirements-semantic.txt installed (not part of the daily
pipeline's requirements.txt -- see that file for why).
"""

from pathlib import Path

import numpy as np
import pandas as pd

MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_PATH = DATA_DIR / "review_embeddings.npz"

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _load_cache() -> dict[str, np.ndarray]:
    if not CACHE_PATH.exists():
        return {}
    data = np.load(CACHE_PATH, allow_pickle=False)
    ids = data["review_ids"]
    vecs = data["vectors"]
    return {str(rid): vec for rid, vec in zip(ids, vecs)}


def _save_cache(id_to_vec: dict[str, np.ndarray]) -> None:
    ids = np.array(list(id_to_vec.keys()))
    vecs = np.array(list(id_to_vec.values()), dtype=np.float32)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE_PATH, review_ids=ids, vectors=vecs)


def get_embeddings(df: pd.DataFrame, text_col: str = "text", id_col: str = "review_id") -> dict[str, np.ndarray]:
    """Returns {review_id: embedding} for every row in df, embedding only the
    review_ids not already in the on-disk cache and writing the merged cache
    back out. Rows with missing/empty text are skipped."""
    cache = _load_cache()
    rows = df[[id_col, text_col]].dropna(subset=[text_col])
    rows = rows[rows[text_col].str.strip() != ""]

    to_embed = rows[~rows[id_col].astype(str).isin(cache.keys())]
    if len(to_embed) > 0:
        model = _get_model()
        texts = to_embed[text_col].tolist()
        new_vecs = model.encode(texts, show_progress_bar=len(texts) > 200, normalize_embeddings=True)
        for rid, vec in zip(to_embed[id_col].astype(str), new_vecs):
            cache[rid] = vec.astype(np.float32)
        _save_cache(cache)
        print(f"Embedded {len(to_embed)} new review(s); {len(cache)} total cached.")
    else:
        print(f"All {len(rows)} review(s) already embedded; nothing new.")

    wanted_ids = set(rows[id_col].astype(str))
    return {rid: vec for rid, vec in cache.items() if rid in wanted_ids}


def embed_query(text: str) -> np.ndarray:
    model = _get_model()
    return model.encode([text], normalize_embeddings=True)[0].astype(np.float32)
