"""Compute cosine and reject zero vectors.

Run: uv run python modules/01_vectors_similarity/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/01_vectors_similarity/solutions/01_practice.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import numpy as np


def solve(left: list[float], right: list[float]) -> float:
    # KEY IDEA: this reference implements the stated acceptance policy.
    left, right = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator == 0:
        raise ValueError("Cosine needs nonzero vectors")
    return float(np.dot(left, right) / denominator)


def main() -> None:
    print(solve([1.0, 0.0], [1.0, 1.0]))


if __name__ == "__main__":
    main()
