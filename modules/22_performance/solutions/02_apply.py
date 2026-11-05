"""Select a feasible operating point.
Each trial is [nprobe,recall,p95_ms]. Return the smallest nprobe satisfying both targets; return null/None if none is feasible. Only development trials belong here.
Run: uv run python modules/22_performance/solutions/02_apply.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/22_performance/exercises/02_apply.py
"""


def solve(trials, min_recall, max_p95):
    return min((p for p, r, t in trials if r >= min_recall and t <= max_p95), default=None)


def main():
    print(solve(*[[[1, 0.6, 2], [4, 0.92, 7], [8, 0.98, 12]], 0.9, 10]))


if __name__ == "__main__":
    main()
