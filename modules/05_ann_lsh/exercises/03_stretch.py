"""Measure candidate coverage.

Run: uv run python modules/05_ann_lsh/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/05_ann_lsh/exercises/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(expected, candidates):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return float(bool(candidates))


def main():
    print(solve([1, 2], [1, 1]))


if __name__ == "__main__":
    main()
