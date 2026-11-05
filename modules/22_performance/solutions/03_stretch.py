"""Count failed requests honestly.
Return [total,failed,overloaded], counting every non-2xx response as failed and status429 as overloaded. Errors are not removed from the denominator.
Run: uv run python modules/22_performance/solutions/03_stretch.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/22_performance/exercises/03_stretch.py
"""


def solve(statuses):
    return [len(statuses), sum(not 200 <= s < 300 for s in statuses), statuses.count(429)]


def main():
    print(solve(*[[200, 200, 429, 503]]))


if __name__ == "__main__":
    main()
