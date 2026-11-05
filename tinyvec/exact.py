"""Small complete exact-kNN kernel used in the first geometry lesson."""

import numpy as np

from tinyvec.metrics import scores


def exact_knn(
    matrix: np.ndarray, query: np.ndarray, ids: list[str], k: int = 5, metric: str = "cosine"
) -> list[tuple[str, float]]:
    values = np.asarray(matrix, dtype=np.float32)
    query = np.asarray(query, dtype=np.float32)
    if values.ndim != 2 or query.shape != (values.shape[1],) or len(ids) != len(values):
        raise ValueError("Expected N by D vectors, a D-vector query, and N IDs")
    if len(set(ids)) != len(ids) or any(not isinstance(key, str) or not key for key in ids):
        raise ValueError("IDs must be unique nonempty strings")
    if not np.isfinite(values).all() or not np.isfinite(query).all():
        raise ValueError("Vectors must be finite")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    if metric == "cosine" and (
        np.linalg.norm(query) == 0 or np.any(np.linalg.norm(values, axis=1) == 0)
    ):
        raise ValueError("Cosine needs nonzero vectors")
    # KEY IDEA: compute one score per row, then retain the best k with an ID tie-break.
    ranked = sorted(
        zip(ids, scores(values, query, metric).tolist(), strict=True),
        key=lambda item: (-item[1], item[0]),
    )
    return ranked[:k]
