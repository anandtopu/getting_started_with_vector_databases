"""Recover a transaction at its savepoint.
Run: uv run python modules/12_pgvector/exercises/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(saved, changes, commit):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return {**saved, **changes}


def main() -> None:
    print(solve({"a": 1}, {"a": 2}, False))


if __name__ == "__main__":
    main()
