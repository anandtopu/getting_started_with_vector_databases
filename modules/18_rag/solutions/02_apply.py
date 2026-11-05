"""Apply: count passage coverage once.

Return the fraction of relevant passage IDs covered by retrieved chunks. Duplicate chunks from a passage earn no extra credit. Empty relevance returns zero.
Run: uv run python modules/18_rag/solutions/02_apply.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(found, relevant):
    # KEY IDEA: Return the fraction of relevant passage IDs covered by retrieved chunks.
    truth = set(relevant)
    return len(set(found) & truth) / len(truth) if truth else 0.0


def main() -> None:
    print(solve(*[["p1", "p1"], ["p1", "p2"]]))


if __name__ == "__main__":
    main()
