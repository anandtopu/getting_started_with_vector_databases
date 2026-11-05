"""Higher scores are always better; L2 scores are negative Euclidean distances."""

import numpy as np


def scores(matrix: np.ndarray, query: np.ndarray, metric: str) -> np.ndarray:
    if metric == "cosine":
        return (matrix @ query) / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(query))
    if metric == "dot":
        return matrix @ query
    if metric == "l2":
        return -np.linalg.norm(matrix - query, axis=1)
    raise ValueError(f"Unknown metric: {metric}")
