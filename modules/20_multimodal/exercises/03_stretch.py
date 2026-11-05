"""Stretch: self-match-free relevance.

Remove the query ID from rankings and relevance before computing recall@k over all eligible relevant IDs. Deduplicate retrieved IDs. Return null when no relevant items remain.
Run: uv run python modules/20_multimodal/exercises/03_stretch.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(found, relevant, query_id, k):
    # YOUR CODE HERE: improve the baseline to meet every criterion.
    return float(bool(set(found[:k]) & set(relevant)))


def main() -> None:
    print(solve(*[["self", "a", "a", "b"], ["self", "a", "b"], "self", 1]))


if __name__ == "__main__":
    main()
