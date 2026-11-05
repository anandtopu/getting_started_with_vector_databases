"""Return bytes for packed sign codes only, rounding dimension bits up for each row.
Run: uv run python modules/bonus/B4_whats_new/solutions/02_apply.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(rows, dimensions):
    return rows * ((dimensions + 7) // 8)


def main() -> None:
    print(solve(*[100, 64]))


if __name__ == "__main__":
    main()
