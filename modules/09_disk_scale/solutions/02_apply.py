"""Count touched pages.

Run: uv run python modules/09_disk_scale/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/09_disk_scale/solutions/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(offset, length, page):
    return (offset + length - 1) // page - offset // page + 1 if length else 0


def main():
    print(solve(4095, 2, 4096))


if __name__ == "__main__":
    main()
