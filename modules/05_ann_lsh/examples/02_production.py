"""Search binary codes with FAISS IndexLSH.

Concepts: Search binary codes with FAISS IndexLSH.
Run: uv run --extra libs python modules/05_ann_lsh/examples/02_production.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: libs
import faiss

from common.index_lessons import unit_catalog


def main():
    products, matrix, q = unit_catalog(640)
    faiss.omp_set_num_threads(1)
    index = faiss.IndexLSH(matrix.shape[1], 64)
    index.add(matrix)
    distances, rows = index.search(q[None, :], 10)
    print(
        "Hamming distances", distances[0], "candidate products", products.iloc[rows[0]].id.tolist()
    )
    assert all(distances[0][:-1] <= distances[0][1:])


if __name__ == "__main__":
    main()
