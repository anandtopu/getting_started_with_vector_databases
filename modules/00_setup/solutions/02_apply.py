"""Count unique listing IDs independently of row count.

Run: uv run python modules/00_setup/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/00_setup/solutions/02_apply.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(rows: list[dict]) -> dict:
    # KEY IDEA: this reference implements the stated acceptance policy.
    return {"rows": len(rows), "unique_ids": len({r["id"] for r in rows})}


def main() -> None:
    print(solve([{"id": "a"}, {"id": "a"}]))


if __name__ == "__main__":
    main()
