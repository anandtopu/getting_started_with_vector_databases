"""Return the complete newline-terminated prefix of a WAL string. Do not silently repair a corrupt complete record.
Run: uv run python modules/bonus/B2_tinyvec_service/exercises/03_stretch.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(data):
    # YOUR CODE HERE: implement the documented contract.
    return None


def main() -> None:
    print(solve(*["a\nb\npartial"]))


if __name__ == "__main__":
    main()
