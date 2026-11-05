"""Gate model publication.
Return new only when readiness is true and 0 <= minimum <= measured <= 1; otherwise preserve old. Do not confuse dimensional compatibility with model-space identity.
Run: uv run python modules/21_operations/exercises/03_stretch.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/21_operations/exercises/03_stretch.py
"""


def solve(ready, measured, minimum, old, new):
    # YOUR CODE HERE: replace the runnable placeholder.
    return None


def main():
    print(solve(*[True, 0.92, 0.9, "blue", "green"]))


if __name__ == "__main__":
    main()
