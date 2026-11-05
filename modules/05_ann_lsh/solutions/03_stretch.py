"""Measure candidate coverage.

Run: uv run python modules/05_ann_lsh/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/05_ann_lsh/solutions/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(expected, candidates):
    return len(set(expected) & set(candidates)) / len(set(expected)) if expected else None


def main():
    print(solve([1, 2], [1, 1]))


if __name__ == "__main__":
    main()
