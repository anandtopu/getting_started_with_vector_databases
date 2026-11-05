"""Compute cosine and reject zero vectors.

Run: uv run python modules/01_vectors_similarity/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/01_vectors_similarity/exercises/01_practice.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import numpy as np


def solve(left: list[float], right: list[float]) -> float:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return float(np.dot(left, right))


def main() -> None:
    print(solve([1.0, 0.0], [1.0, 1.0]))


if __name__ == "__main__":
    main()
