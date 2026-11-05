"""Split inputs into bounded ordered batches.

Run: uv run python modules/02_embeddings/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/02_embeddings/exercises/02_apply.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(items: list[str], size: int) -> list[list[str]]:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return [items] if items else []


def main() -> None:
    print(solve(["mug", "chair", "lamp"], 2))


if __name__ == "__main__":
    main()
