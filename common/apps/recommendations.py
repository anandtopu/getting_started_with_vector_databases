"""Marlowe v4: time-bounded event profiles and maximum marginal relevance."""

import numpy as np

from common.embeddings import normalize

WEIGHTS = {"view": 1.0, "cart": 3.0, "purchase": 5.0}


def user_profile(events, vectors_by_id, cutoff: str):
    """ISO UTC timestamps make a fixed, strictly earlier training boundary explicit."""
    selected = [
        e
        for e in events
        if e["timestamp"] < cutoff and e["product_id"] in vectors_by_id and e["action"] in WEIGHTS
    ]
    if not selected:
        return None, set()
    # KEY IDEA: future events never contribute to the query vector.
    vector = sum(WEIGHTS[e["action"]] * vectors_by_id[e["product_id"]] for e in selected)
    if np.linalg.norm(vector) == 0:
        return None, set()
    return normalize(vector), {e["product_id"] for e in selected}


def mmr(ids, vectors, query, k: int = 10, relevance: float = 0.7):
    if not 0 <= relevance <= 1 or k < 0 or len(ids) != len(set(ids)):
        raise ValueError("Unique IDs, k >= 0 and relevance in [0, 1] required")
    matrix = normalize(vectors)
    q = normalize(query)
    if len(ids) != len(matrix):
        raise ValueError("IDs and vectors must align")
    selected = []
    remaining = set(range(len(ids)))
    similarities = matrix @ q
    while remaining and len(selected) < k:

        def score(i):
            redundancy = float((matrix[i] @ matrix[selected].T).max()) if selected else 0.0
            return relevance * float(similarities[i]) - (1 - relevance) * redundancy

        best = min(remaining, key=lambda i: (-score(i), ids[i]))
        selected.append(best)
        remaining.remove(best)
    return [ids[i] for i in selected]


def recommend(search, query, *, exclude=(), k=10, relevance=0.7):
    excluded = set(exclude)
    # Retrieve enough candidates to remove seen items without silently shrinking k.
    candidates = search.store.search(
        query, min(len(search.records), max(k * 5, k + len(excluded))), space=search.space
    )
    ids = [h.id for h in candidates if h.id not in excluded]
    if not ids:
        return []
    vectors = np.stack([search.by_id[key].vector for key in ids])
    return mmr(ids, vectors, query, k, relevance)


def diversity(ids, vectors_by_id):
    if len(ids) < 2:
        return 0.0
    matrix = normalize(np.stack([vectors_by_id[key] for key in ids]))
    distances = 1 - matrix @ matrix.T
    return float(distances[np.triu_indices(len(ids), 1)].mean())
