"""Given [parameter,recall] development trials, select the smallest parameter meeting target or null.
Run: uv run python modules/bonus/B3_research_benchmarks/solutions/02_apply.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(trials, target):
    return min((p for p, r in trials if r >= target), default=None)


def main() -> None:
    print(solve(*[[[8, 0.8], [32, 0.97], [64, 1]], 0.95]))


if __name__ == "__main__":
    main()
