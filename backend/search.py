import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import json
from backend.database import Database
from backend.embeddings import encode_text, encode_image

# FAISS is an optional dependency at import time; defer loading so the module
# can be imported in environments without FAISS installed.
try:
    import faiss
    _HAS_FAISS = True
except Exception:
    faiss = None
    _HAS_FAISS = False

# lazy-loaded globals
faiss_index = None
id_map = None


def _ensure_faiss_index_loaded():
    global faiss_index, id_map
    if faiss_index is not None:
        return

    if not _HAS_FAISS:
        raise ImportError(
            "FAISS is required for dense search. Install faiss and retry.\n"
            "On Windows you may need to follow faiss installation instructions."
        )

    faiss_index = faiss.read_index("indexes/faiss_index.bin")

    if os.path.exists("indexes/id_map.npy"):
        id_map = np.load("indexes/id_map.npy")
    else:
        db = Database()
        product_ids = [product[0] for product in db.get_all_products()]
        db.close()
        if len(product_ids) != faiss_index.ntotal:
            raise FileNotFoundError(
                "indexes/id_map.npy is missing and could not be reconstructed "
                f"from products.db ({len(product_ids)} products for "
                f"{faiss_index.ntotal} FAISS vectors). Rebuild the FAISS index."
            )
        id_map = np.array(product_ids)


_bm25 = None
_bm25_ids = None


def _ensure_bm25_loaded():
    global _bm25, _bm25_ids
    if _bm25 is not None and _bm25_ids is not None:
        return

    try:
        from backend.bm25_search import load_bm25_index
    except Exception:
        raise ImportError(
            "BM25 dependencies are missing. Install 'rank_bm25' to use sparse search."
        )

    bm25_data = load_bm25_index()
    _bm25 = bm25_data["bm25"]
    _bm25_ids = bm25_data["product_ids"]

def compose_query(image_path=None, text=None, image_weight=0.7):
    vectors = []
    weights = []

    if image_path:
        image_vec = encode_image(image_path)
        if image_vec is not None:
            vectors.append(image_vec)
            weights.append(image_weight)

    if text:
        text_vec = encode_text(text)
        if text_vec is not None:
            vectors.append(text_vec)
            weights.append(1.0 - image_weight)

    if not vectors:
        raise ValueError("Must provide image, text, or both")

    query_vector = sum(v * w for v, w in zip(vectors, weights))
    query_vector = query_vector / np.linalg.norm(query_vector)
    return query_vector.reshape(1, -1).astype('float32')


def hybrid_search(query_text=None, query_image=None,
                  image_weight=0.7, top_k=10, alpha=0.6,
                  gender=None):  
    # compose query vector
    query_vector = compose_query(
        image_path=query_image,
        text=query_text,
        image_weight=image_weight
    )

    # dense search via FAISS
    _ensure_faiss_index_loaded()
    faiss_index.nprobe = 10
    distances, indices = faiss_index.search(query_vector, 50)

    dense_scores = {}
    for rank, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        pid = int(id_map[idx])
        dense_scores[pid] = 1 / (rank + 1)

    # sparse search via BM25
    sparse_scores = {}
    if query_text:
        _ensure_bm25_loaded()
        tokens = query_text.lower().split()
        bm25_raw = _bm25.get_scores(tokens)
        top50 = np.argsort(bm25_raw)[-50:][::-1]
        for idx in top50:
            pid = _bm25_ids[idx]
            sparse_scores[pid] = float(bm25_raw[idx])

        # normalize sparse scores to 0-1
        max_score = max(sparse_scores.values()) if sparse_scores else 1
        if max_score > 0:
            sparse_scores = {
                pid: score / max_score
                for pid, score in sparse_scores.items()
            }

    # combine scores
    all_ids = set(dense_scores) | set(sparse_scores)
    final_scores = {}
    for pid in all_ids:
        d = dense_scores.get(pid, 0)
        s = sparse_scores.get(pid, 0)
        final_scores[pid] = alpha * d + (1 - alpha) * s

    ranked = sorted(
        final_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    # fetch product details
    db = Database()
    results = []
    for pid, score in ranked:
        product = db.get_product_by_id(int(pid))
        if product:
            # filter by gender if specified
            if gender and product[2].lower() != gender.lower():
                continue
            results.append({
                "id": product[0],
                "name": product[1],
                "gender": product[2],
                "category": product[4],
                "article_type": product[5],
                "colour": product[6],
                "image_path": product[9],
                "score": round(score, 4)
            })
    db.close()
    return results
