"""Compute set recall with duplicate found IDs ignored; return null if ground truth is empty.
Run: uv run python modules/bonus/B3_research_benchmarks/exercises/01_practice.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(found, truth):
    # YOUR CODE HERE: implement the documented contract.
    return None


def main() -> None:
    print(solve(*[["a", "a", "b"], ["a", "c"]]))


if __name__ == "__main__":
    main()
