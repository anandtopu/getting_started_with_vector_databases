"""Compare multi-vector similarity.
Run: uv run python modules/13_qdrant/exercises/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(scores):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return max(scores[0]) if scores else 0


def main() -> None:
    print(solve([[1, 0], [0, 1]]))


if __name__ == "__main__":
    main()
