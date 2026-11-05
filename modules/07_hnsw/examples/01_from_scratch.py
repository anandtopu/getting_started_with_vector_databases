"""Walk a layered product graph and inspect its edges.

Concepts: Walk a layered product graph and inspect its edges.
Run: uv run python modules/07_hnsw/examples/01_from_scratch.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import unit_catalog
from tinyvec.hnsw import HNSW


def main():
    products, matrix, query = unit_catalog(220)
    graph = HNSW(matrix, M=6, efConstruction=24, efSearch=24)
    print("layer populations", [len(layer) for layer in graph.layers], "entry", graph.entry)
    candidates = graph.candidates(query, 10)
    print(
        "entry product",
        products.iloc[graph.entry].title,
        "found",
        products.iloc[candidates[:3]].title.tolist(),
    )
    assert all(len(edges) <= 6 for layer in graph.layers for edges in layer.values())


if __name__ == "__main__":
    main()
