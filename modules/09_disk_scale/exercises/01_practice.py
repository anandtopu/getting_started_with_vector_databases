"""Bound each scan block.

Run: uv run python modules/09_disk_scale/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/09_disk_scale/exercises/01_practice.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(rows, block):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return [[0, rows]] if rows else []


def main():
    print(solve(9, 4))


if __name__ == "__main__":
    main()
