"""Train a residual IVF-PQ index with FAISS.

Concepts: Train a residual IVF-PQ index with FAISS.
Run: uv run --extra libs python modules/08_quantization/examples/02_production.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: libs
import faiss
import numpy as np

from common.index_lessons import unit_catalog


def main():
    products, matrix, q = unit_catalog(640)
    faiss.omp_set_num_threads(1)
    index = faiss.IndexIVFPQ(
        faiss.IndexFlatIP(matrix.shape[1]), matrix.shape[1], 8, 8, 3, faiss.METRIC_INNER_PRODUCT
    )
    index.train(matrix)
    index.add(matrix)
    index.nprobe = 4
    _, labels = index.search(q[None, :], 40)
    candidates = labels[0][labels[0] >= 0]
    reranked = candidates[np.argsort(-(matrix[candidates] @ q), kind="stable")[:10]]
    print(
        "compressed leaders",
        products.iloc[candidates[:10]].id.tolist(),
        "after rescoring",
        products.iloc[reranked].id.tolist(),
    )
    print("packed residual bytes per row", index.code_size)
    assert len(reranked) == 10


if __name__ == "__main__":
    main()
