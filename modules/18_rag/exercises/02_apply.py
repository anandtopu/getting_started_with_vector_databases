"""Apply: count passage coverage once.

Return the fraction of relevant passage IDs covered by retrieved chunks. Duplicate chunks from a passage earn no extra credit. Empty relevance returns zero.
Run: uv run python modules/18_rag/exercises/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(found, relevant):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return float(bool(set(found) & set(relevant)))


def main() -> None:
    print(solve(*[["p1", "p1"], ["p1", "p2"]]))


if __name__ == "__main__":
    main()
