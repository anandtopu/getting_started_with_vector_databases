"""Compare FAISS and USearch graph candidates.

Concepts: Compare FAISS and USearch graph candidates.
Run: uv run --extra libs python modules/07_hnsw/examples/02_production.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: libs
import faiss
import numpy as np
from usearch.index import Index

from common.index_lessons import unit_catalog


def main():
    products, matrix, q = unit_catalog(640)
    faiss.omp_set_num_threads(1)
    index = faiss.IndexHNSWFlat(matrix.shape[1], 8, faiss.METRIC_INNER_PRODUCT)
    index.hnsw.efConstruction = 32
    index.hnsw.efSearch = 24
    index.add(matrix)
    _, rows = index.search(q[None, :], 10)
    native = Index(
        ndim=matrix.shape[1],
        metric="cos",
        dtype="f32",
        connectivity=8,
        expansion_add=32,
        expansion_search=24,
    )
    native.add(np.arange(len(matrix), dtype=np.uint64), matrix, threads=1)
    matches = native.search(q, 10, threads=1)
    print(
        "FAISS",
        products.iloc[rows[0]].id.tolist(),
        "USearch",
        products.iloc[matches.keys].id.tolist(),
    )
    assert len(matches.keys) == len(rows[0]) == 10


if __name__ == "__main__":
    main()
