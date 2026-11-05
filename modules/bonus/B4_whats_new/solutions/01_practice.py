"""Return sign codes with zero assigned to +1, matching the reference quantizer.
Run: uv run python modules/bonus/B4_whats_new/solutions/01_practice.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(values):
    return [1 if value >= 0 else -1 for value in values]


def main() -> None:
    print(solve(*[[-1, 0, 2]]))


if __name__ == "__main__":
    main()
