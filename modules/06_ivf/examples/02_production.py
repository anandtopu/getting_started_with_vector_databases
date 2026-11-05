"""Probe a trained FAISS inverted file.

Concepts: Probe a trained FAISS inverted file.
Run: uv run --extra libs python modules/06_ivf/examples/02_production.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: libs
import faiss

from common.index_lessons import unit_catalog


def main():
    products, matrix, q = unit_catalog(640)
    faiss.omp_set_num_threads(1)
    coarse = faiss.IndexFlatIP(matrix.shape[1])
    index = faiss.IndexIVFFlat(coarse, matrix.shape[1], 8, faiss.METRIC_INNER_PRODUCT)
    index.train(matrix)
    index.add(matrix)
    index.nprobe = 3
    scores, rows = index.search(q[None, :], 10)
    print("occupancies", [index.invlists.list_size(i) for i in range(8)])
    print("candidate products", products.iloc[rows[0]].id.tolist(), "cosine scores", scores[0])
    assert index.is_trained and index.ntotal == len(matrix)


if __name__ == "__main__":
    main()
