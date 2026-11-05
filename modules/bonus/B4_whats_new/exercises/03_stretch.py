"""Exact-rerank only the supplied unique candidate IDs; return the k smallest squared distances, breaking ties by ID.
Run: uv run python modules/bonus/B4_whats_new/exercises/03_stretch.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(candidate_ids, distances, k):
    # YOUR CODE HERE: implement the documented contract.
    return None


def main() -> None:
    print(solve(*[[2, 0, 2], [0.1, 0, 0.3], 2]))


if __name__ == "__main__":
    main()
