"""Choose a measured probe budget.

Run: uv run python modules/06_ivf/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/06_ivf/solutions/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(runs, floor):
    valid = [r for r in runs if r[1] >= floor]
    return max(valid, key=lambda r: r[2])[0] if valid else None


def main():
    print(solve([(1, 0.6, 300), (4, 0.9, 200)], 0.85))


if __name__ == "__main__":
    main()
