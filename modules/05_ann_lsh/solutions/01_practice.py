"""Signature bits.

Run: uv run python modules/05_ann_lsh/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/05_ann_lsh/solutions/01_practice.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(components):
    return [x >= 0 for x in components]


def main():
    print(solve([1, -2, 0]))


if __name__ == "__main__":
    main()
