"""Intersect metadata postings.

Run: uv run python modules/10_filtering_hybrid/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/10_filtering_hybrid/solutions/01_practice.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(region, stock):
    return sorted(set(region) & set(stock))


def main():
    print(solve([1, 2], [2, 3]))


if __name__ == "__main__":
    main()
