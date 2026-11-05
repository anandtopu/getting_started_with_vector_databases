"""Choose a measured probe budget.

Run: uv run python modules/06_ivf/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/06_ivf/exercises/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(runs, floor):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return runs[0][0] if runs else None


def main():
    print(solve([(1, 0.6, 300), (4, 0.9, 200)], 0.85))


if __name__ == "__main__":
    main()
