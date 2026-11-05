"""Split inputs into bounded ordered batches.

Run: uv run python modules/02_embeddings/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/02_embeddings/solutions/02_apply.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(items: list[str], size: int) -> list[list[str]]:
    # KEY IDEA: this reference implements the stated acceptance policy.
    if size < 1:
        raise ValueError("Batch size must be positive")
    return [items[start : start + size] for start in range(0, len(items), size)]


def main() -> None:
    print(solve(["mug", "chair", "lamp"], 2))


if __name__ == "__main__":
    main()
