"""Gather probed lists.

Run: uv run python modules/06_ivf/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/06_ivf/exercises/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(lists, probes):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return list(lists[0]) if lists else []


def main():
    print(solve([[2], [4, 5]], [1]))


if __name__ == "__main__":
    main()
