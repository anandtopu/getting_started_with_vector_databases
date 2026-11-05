"""Apply a recall and latency budget.
Run: uv run python modules/16_landscape/solutions/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, floor, budget):
    return sorted(name for name, recall, p95 in rows if recall >= floor and p95 <= budget)


def main() -> None:
    print(solve([["A", 0.9, 7]], 0.9, 8))


if __name__ == "__main__":
    main()
