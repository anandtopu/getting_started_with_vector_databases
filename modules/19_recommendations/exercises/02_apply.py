"""Apply: greedy diversity.

Use each row's relevance and a redundancy matrix. Repeatedly maximize weight*relevance - (1-weight)*maximum similarity to already selected rows. Break ties by index.
Run: uv run python modules/19_recommendations/exercises/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(relevance, similarities, weight, k):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return sorted(range(len(relevance)), key=lambda i: (-relevance[i], i))[:k]


def main() -> None:
    print(solve(*[[1, 0.99, 0.5], [[1, 1, 0], [1, 1, 0], [0, 0, 1]], 0.2, 2]))


if __name__ == "__main__":
    main()
