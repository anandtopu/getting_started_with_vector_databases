"""Return true only if complete WAL sequence numbers start at one and have no gaps or duplicates.
Run: uv run python modules/bonus/B2_tinyvec_service/solutions/01_practice.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(sequences):
    return sequences == list(range(1, len(sequences) + 1))


def main() -> None:
    print(solve(*[[1, 2, 3]]))


if __name__ == "__main__":
    main()
