"""Apply: greedy diversity.

Use each row's relevance and a redundancy matrix. Repeatedly maximize weight*relevance - (1-weight)*maximum similarity to already selected rows. Break ties by index.
Run: uv run python modules/19_recommendations/solutions/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(relevance, similarities, weight, k):
    # KEY IDEA: Use each row's relevance and a redundancy matrix.
    selected = []
    while len(selected) < min(k, len(relevance)):
        candidates = [i for i in range(len(relevance)) if i not in selected]

        def score(i):
            redundant = max((similarities[i][j] for j in selected), default=0)
            return weight * relevance[i] - (1 - weight) * redundant

        selected.append(min(candidates, key=lambda i: (-score(i), i)))
    return selected


def main() -> None:
    print(solve(*[[1, 0.99, 0.5], [[1, 1, 0], [1, 1, 0], [0, 0, 1]], 0.2, 2]))


if __name__ == "__main__":
    main()
