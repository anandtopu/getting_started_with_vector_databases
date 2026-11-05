"""Key cached embeddings by content and complete model identity.

Run: uv run python modules/02_embeddings/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/02_embeddings/exercises/01_practice.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

from common.io import digest


def solve(text: str, spec: dict, role: str) -> str:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return digest(text)


def main() -> None:
    print(solve("coffee", {"revision": "one", "dimensions": 3}, "query"))


if __name__ == "__main__":
    main()
