"""Filter eligible stock before choosing top k.

Run: uv run python modules/03_tinyvec/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/03_tinyvec/exercises/02_apply.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(rows: list[dict], k: int) -> list[str]:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    ranked = sorted(rows, key=lambda r: (-r["score"], r["id"]))
    return [r["id"] for r in ranked[:k] if r["stock"] > 0]


def main() -> None:
    print(solve([{"id": "a", "score": 1.0, "stock": 0}, {"id": "b", "score": 0.9, "stock": 2}], 1))


if __name__ == "__main__":
    main()
