"""Recover a transaction at its savepoint.
Run: uv run python modules/12_pgvector/solutions/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(saved, changes, commit):
    return {**saved, **changes} if commit else dict(saved)


def main() -> None:
    print(solve({"a": 1}, {"a": 2}, False))


if __name__ == "__main__":
    main()
