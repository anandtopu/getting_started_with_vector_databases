"""Apply a recall and latency budget.
Run: uv run python modules/16_landscape/exercises/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, floor, budget):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return [r[0] for r in rows]


def main() -> None:
    print(solve([["A", 0.9, 7]], 0.9, 8))


if __name__ == "__main__":
    main()
