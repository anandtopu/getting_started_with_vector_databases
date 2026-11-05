"""Detect lost or changed rows after restore.
Run: uv run python modules/11_embedded/exercises/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(before, after):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return sorted(set(before) - set(after))


def main() -> None:
    print(solve({"a": 1, "b": 2}, {"b": 3}))


if __name__ == "__main__":
    main()
