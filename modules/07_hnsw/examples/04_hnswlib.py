"""Build and search the optional native hnswlib graph.

Concepts: Build and search the optional native hnswlib graph.
Run: uv run --extra hnswlib python modules/07_hnsw/examples/04_hnswlib.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: hnswlib
from common.index_lessons import trial


def main():
    result = trial("hnswlib", M=8, efConstruction=40, efSearch=32)
    print(result)
    assert len(result["ids"]) == 10
    import hnswlib

    from common.index_lessons import unit_catalog

    _, matrix, _ = unit_catalog(160)
    graph = hnswlib.Index(space="cosine", dim=matrix.shape[1])
    graph.init_index(max_elements=len(matrix), M=8, ef_construction=32, random_seed=42)
    graph.add_items(matrix, num_threads=1)
    graph.mark_deleted(0)
    labels, _ = graph.knn_query(matrix[0], k=10, num_threads=1)
    assert 0 not in labels[0]
    print("tombstoned row 0; surviving neighbors", labels[0])


if __name__ == "__main__":
    main()
