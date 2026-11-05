"""Build a region payload posting.
Run: uv run python modules/13_qdrant/exercises/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, region):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return [r[0] for r in rows]


def main() -> None:
    print(solve([["a", "north"]], "north"))


if __name__ == "__main__":
    main()
