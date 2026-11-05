"""Retire an item from a native USearch graph.

Run: uv run --extra libs python modules/07_hnsw/examples/05_deletions.py
Expected: compare the reported ranking and verify the final assertion.
CPU: seconds, included data, no Docker or model downloads.
"""

# course-extra: libs
import numpy as np
from usearch.index import Index

from common.index_lessons import unit_catalog


def main():
    _, matrix, _ = unit_catalog(100)
    index = Index(ndim=matrix.shape[1], metric="cos", dtype="f32")
    index.add(np.arange(len(matrix), dtype=np.uint64), matrix, threads=1)
    index.remove(0)
    after = index.search(matrix[0], 10, threads=1).keys.tolist()
    print("survivors", after)
    assert 0 not in after and len(index) == 99


if __name__ == "__main__":
    main()
