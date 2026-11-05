"""Choose a metric-matched SQL distance operator.
Run: uv run python modules/12_pgvector/exercises/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(metric):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return "<->"


def main() -> None:
    print(solve("cosine"))


if __name__ == "__main__":
    main()
