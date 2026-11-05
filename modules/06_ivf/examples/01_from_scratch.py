"""Trace a centroid assignment from training to retrieval.

Concepts: Trace a centroid assignment from training to retrieval.
Run: uv run python modules/06_ivf/examples/01_from_scratch.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

import numpy as np

from common.index_lessons import unit_catalog
from tinyvec.ivf import IVF


def main():
    _, matrix, query = unit_catalog(320)
    index = IVF(matrix, nlist=8, nprobe=1)
    distances = ((index.centers - query) ** 2).sum(axis=1)
    nearest = int(np.argmin(distances))
    candidates = index.candidates(query, 10)
    print("nearest centroid", nearest, "list sizes", [len(rows) for rows in index.lists])
    assert set(candidates) == set(index.lists[nearest])
    index.nprobe = 8
    assert set(index.candidates(query, 10)) == set(range(len(matrix)))


if __name__ == "__main__":
    main()
