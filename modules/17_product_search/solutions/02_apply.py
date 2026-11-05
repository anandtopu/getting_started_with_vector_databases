"""Apply: filter both hybrid branches.

Remove IDs outside the eligible set from every ranking before returning the first k fused IDs. Use reciprocal rank fusion with constant 60.
Run: uv run python modules/17_product_search/solutions/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(rankings, eligible, k):
    # KEY IDEA: Remove IDs outside the eligible set from every ranking before returning the first k fused IDs.
    from tinyvec.hybrid import fuse

    allowed = set(eligible)
    return [
        key for key, _ in fuse([[key for key in ranking if key in allowed] for ranking in rankings])
    ][:k]


def main() -> None:
    print(solve(*[[["x", "a", "b"], ["b", "x", "a"]], ["a", "b"], 2]))


if __name__ == "__main__":
    main()
