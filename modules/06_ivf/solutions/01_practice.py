"""Assign to a centroid.

Run: uv run python modules/06_ivf/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/06_ivf/solutions/01_practice.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(value, centers):
    return min(range(len(centers)), key=lambda i: abs(centers[i] - value))


def main():
    print(solve(8, [1, 9]))


if __name__ == "__main__":
    main()
