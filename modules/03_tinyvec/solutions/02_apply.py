"""Filter eligible stock before choosing top k.

Run: uv run python modules/03_tinyvec/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/03_tinyvec/solutions/02_apply.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(rows: list[dict], k: int) -> list[str]:
    # KEY IDEA: this reference implements the stated acceptance policy.
    eligible = [r for r in rows if r["stock"] > 0]
    ranked = sorted(eligible, key=lambda r: (-r["score"], r["id"]))
    return [r["id"] for r in ranked[:k]]


def main() -> None:
    print(solve([{"id": "a", "score": 1.0, "stock": 0}, {"id": "b", "score": 0.9, "stock": 2}], 1))


if __name__ == "__main__":
    main()
