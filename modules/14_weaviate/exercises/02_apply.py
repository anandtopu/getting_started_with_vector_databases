"""Separate tenant objects with repeated IDs.
Run: uv run python modules/14_weaviate/exercises/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, tenant):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return {key: value for _, key, value in rows}


def main() -> None:
    print(solve([["north", "1", "mug"]], "north"))


if __name__ == "__main__":
    main()
