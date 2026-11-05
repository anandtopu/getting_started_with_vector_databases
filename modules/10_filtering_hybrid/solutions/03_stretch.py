"""Score a token interaction.

Run: uv run python modules/10_filtering_hybrid/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/10_filtering_hybrid/solutions/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(scores):
    return sum(max(row) for row in scores)


def main():
    print(solve([[0.1, 0.9], [0.8, 0.2]]))


if __name__ == "__main__":
    main()
