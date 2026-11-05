"""Choose a metric-matched SQL distance operator.
Run: uv run python modules/12_pgvector/solutions/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(metric):
    return {"cosine": "<=>", "dot": "<#>", "l2": "<->", "hamming": "<~>"}[metric]


def main() -> None:
    print(solve("cosine"))


if __name__ == "__main__":
    main()
