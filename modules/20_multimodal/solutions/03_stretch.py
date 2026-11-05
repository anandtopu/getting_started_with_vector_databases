"""Stretch: self-match-free relevance.

Remove the query ID from rankings and relevance before computing recall@k over all eligible relevant IDs. Deduplicate retrieved IDs. Return null when no relevant items remain.
Run: uv run python modules/20_multimodal/solutions/03_stretch.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(found, relevant, query_id, k):
    # KEY IDEA: Remove the query ID from rankings and relevance before computing recall@k over all eligible relevant IDs.
    truth = set(relevant) - {query_id}
    ranked = list(dict.fromkeys(key for key in found if key != query_id))[:k]
    return len(set(ranked) & truth) / len(truth) if truth else None


def main() -> None:
    print(solve(*[["self", "a", "a", "b"], ["self", "a", "b"], "self", 1]))


if __name__ == "__main__":
    main()
