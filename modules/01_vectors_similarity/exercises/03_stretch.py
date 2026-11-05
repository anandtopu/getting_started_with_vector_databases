"""Normalize every row without inventing a direction for zero.

Run: uv run python modules/01_vectors_similarity/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/01_vectors_similarity/exercises/03_stretch.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(matrix: list[list[float]]) -> list[list[float]]:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return matrix


def main() -> None:
    print(solve([[3.0, 4.0], [1.0, 0.0]]))


if __name__ == "__main__":
    main()
