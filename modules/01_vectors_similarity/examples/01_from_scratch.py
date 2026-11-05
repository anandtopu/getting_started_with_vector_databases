"""Build exact nearest-neighbor search from hand features.

Concepts: 2D vectors, dot, cosine, Euclidean, normalization.
Run: uv run python modules/01_vectors_similarity/examples/01_from_scratch.py
Expected: cosine favors mug-warmer; after rescaling, dot favors travel-flask
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import numpy as np

from common.teaching import hand_features
from tinyvec.exact import exact_knn


def main() -> None:
    ids, matrix, query = hand_features()
    print(f"Rows x coordinates: {matrix.shape}; dtype: {matrix.dtype}")
    print("Coordinates: warmth, portability; these are designed features, not learned meanings.")
    for metric in ["dot", "cosine", "l2"]:
        print(metric, exact_knn(matrix, query, ids, 4, metric))
    # KEY IDEA: a longer arrow can win a dot product even when its direction fits less well.
    scaled = matrix.copy()
    scaled[1] *= 3
    print("After multiplying the flask vector by 3:", exact_knn(scaled, query, ids, 1, "dot"))
    unit = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    print("Unit-vector lengths:", np.linalg.norm(unit, axis=1).round(4).tolist())


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
