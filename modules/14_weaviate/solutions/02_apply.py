"""Separate tenant objects with repeated IDs.
Run: uv run python modules/14_weaviate/solutions/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, tenant):
    return {key: value for owner, key, value in rows if owner == tenant}


def main() -> None:
    print(solve([["north", "1", "mug"]], "north"))


if __name__ == "__main__":
    main()
