"""Count touched pages.

Run: uv run python modules/09_disk_scale/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/09_disk_scale/exercises/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(offset, length, page):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return int(length > 0)


def main():
    print(solve(4095, 2, 4096))


if __name__ == "__main__":
    main()
