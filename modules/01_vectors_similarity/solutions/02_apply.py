"""Return exact top k with deterministic ID ties.

Run: uv run python modules/01_vectors_similarity/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/01_vectors_similarity/solutions/02_apply.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import numpy as np

from tinyvec.exact import exact_knn


def solve(matrix: list[list[float]], query: list[float], ids: list[str], k: int) -> list[str]:
    # KEY IDEA: this reference implements the stated acceptance policy.
    return [key for key, _ in exact_knn(np.asarray(matrix), np.asarray(query), ids, k)]


def main() -> None:
    print(solve([[1.0, 0.0], [0.0, 1.0]], [1.0, 0.0], ["a", "b"], 1))


if __name__ == "__main__":
    main()
