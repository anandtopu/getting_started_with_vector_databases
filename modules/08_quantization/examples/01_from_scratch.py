"""Encode each subvector as the address of a learned codeword.

Concepts: Encode each subvector as the address of a learned codeword.
Run: uv run python modules/08_quantization/examples/01_from_scratch.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

import numpy as np

from common.index_lessons import unit_catalog
from tinyvec.pq import PQ


def main():
    _, matrix, q = unit_catalog(320)
    pq = PQ(matrix, parts=8, centroids=16)
    codes = pq.codes[0]
    restored = np.concatenate([book[code] for book, code in zip(pq.books, codes, strict=True)])
    print(
        "first code",
        codes,
        "reconstruction error",
        np.linalg.norm(matrix[0] - restored),
        "payload bytes",
        pq.payload_bytes,
    )
    print("nearest by asymmetric lookup", pq.candidates(q, 5))
    assert pq.codes.shape == (320, 8)


if __name__ == "__main__":
    main()
