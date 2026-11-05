"""Reject equally sized vectors from incompatible spaces.

Run: uv run python modules/02_embeddings/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/02_embeddings/exercises/03_stretch.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(left: dict, right: dict) -> bool:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return left["dimensions"] == right["dimensions"]


def main() -> None:
    print(solve({"dimensions": 384}, {"dimensions": 384}))


if __name__ == "__main__":
    main()
