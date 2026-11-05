"""Check a reopened collection's identity.
Run: uv run python modules/11_embedded/exercises/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(expected, actual):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return expected["dim"] == actual["dim"]


def main() -> None:
    print(solve({"dim": 3, "space": "a"}, {"dim": 3, "space": "b"}))


if __name__ == "__main__":
    main()
