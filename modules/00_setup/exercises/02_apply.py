"""Count unique listing IDs independently of row count.

Run: uv run python modules/00_setup/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/00_setup/exercises/02_apply.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(rows: list[dict]) -> dict:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return {"rows": len(rows), "unique_ids": len(rows)}


def main() -> None:
    print(solve([{"id": "a"}, {"id": "a"}]))


if __name__ == "__main__":
    main()
