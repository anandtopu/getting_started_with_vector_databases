"""Find a visible product revision.
Run: uv run python modules/15_milvus/exercises/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(events, watermark):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return events[-1][1] if events else None


def main() -> None:
    print(solve([[1, "sale"], [3, "retired"]], 2))


if __name__ == "__main__":
    main()
