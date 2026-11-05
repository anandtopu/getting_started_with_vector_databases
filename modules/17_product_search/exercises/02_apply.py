"""Apply: filter both hybrid branches.

Remove IDs outside the eligible set from every ranking before returning the first k fused IDs. Use reciprocal rank fusion with constant 60.
Run: uv run python modules/17_product_search/exercises/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(rankings, eligible, k):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return [key for key in rankings[0] if key in eligible][:k]


def main() -> None:
    print(solve(*[[["x", "a", "b"], ["b", "x", "a"]], ["a", "b"], 2]))


if __name__ == "__main__":
    main()
