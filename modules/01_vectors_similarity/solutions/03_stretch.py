"""Normalize every row without inventing a direction for zero.

Run: uv run python modules/01_vectors_similarity/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/01_vectors_similarity/solutions/03_stretch.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import numpy as np


def solve(matrix: list[list[float]]) -> list[list[float]]:
    # KEY IDEA: this reference implements the stated acceptance policy.
    values = np.asarray(matrix, dtype=float)
    lengths = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(lengths == 0):
        raise ValueError("Zero has no direction")
    return (values / lengths).tolist()


def main() -> None:
    print(solve([[3.0, 4.0], [1.0, 0.0]]))


if __name__ == "__main__":
    main()
