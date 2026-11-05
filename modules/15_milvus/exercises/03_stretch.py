"""Confirm that an index finished building.
Run: uv run python modules/15_milvus/exercises/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(state, indexed, expected):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return state == "Finished"


def main() -> None:
    print(solve("Finished", 50, 100))


if __name__ == "__main__":
    main()
