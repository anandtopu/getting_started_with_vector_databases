"""Compare multi-vector similarity.
Run: uv run python modules/13_qdrant/solutions/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(scores):
    return sum(max(row) for row in scores)


def main() -> None:
    print(solve([[1, 0], [0, 1]]))


if __name__ == "__main__":
    main()
