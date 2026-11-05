"""Fuse sparse lexical matches with a dense ranking.

Concepts: Fuse sparse lexical matches with a dense ranking.
Run: uv run python modules/10_filtering_hybrid/examples/01_from_scratch.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from tinyvec.hybrid import BM25, fuse, maxsim


def main():
    documents = ["waterproof hiking boots SKU-7", "boots for wet trails", "linen shirt"]
    lexical = BM25(documents).rank("SKU-7")
    dense = [1, 0, 2]
    fused = fuse([dense, lexical])
    print("lexical", lexical, "dense", dense, "fused", fused)
    assert fused[0][0] == 0
    # Each query token chooses its own strongest document token.
    assert maxsim([[1, 0], [0, 1]], [[1, 0], [0, 1]]) == 2


if __name__ == "__main__":
    main()
