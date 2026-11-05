"""Stable identity replay.
Keep the last value for each (tenant, source_id), and return sorted [tenant, source_id, value] rows. An update replaces a value; two tenants may reuse the same source ID.
Run: uv run python modules/21_operations/solutions/01_practice.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/21_operations/exercises/01_practice.py
"""


def solve(rows):
    return sorted([[t, s, v] for (t, s), v in {(r[0], r[1]): r[2] for r in rows}.items()])


def main():
    print(solve(*[[["a", "x", 1], ["a", "x", 2], ["b", "x", 3]]]))


if __name__ == "__main__":
    main()
