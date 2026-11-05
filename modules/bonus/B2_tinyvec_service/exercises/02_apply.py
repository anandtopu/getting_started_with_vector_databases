"""Given [sequence,value] entries, return values strictly after a checkpoint watermark.
Run: uv run python modules/bonus/B2_tinyvec_service/exercises/02_apply.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(entries, watermark):
    # YOUR CODE HERE: implement the documented contract.
    return None


def main() -> None:
    print(solve(*[[[1, "a"], [2, "b"], [3, "c"]], 2]))


if __name__ == "__main__":
    main()
