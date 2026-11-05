"""Trace bounded disk graph reads and compare two fragment layouts.
Run: uv run python modules/09_disk_scale/examples/04_page_reads.py
CPU: seconds. Uses a temporary graph over included product vectors. No Docker or remote storage.
"""

import tempfile
from pathlib import Path

import numpy as np

from common.index_lessons import unit_catalog
from common.teaching import evidence
from tinyvec.hnsw import HNSW


def main():
    products, matrix, q = unit_catalog(240)
    graph = HNSW(matrix, M=6, efConstruction=24)
    # Keep compact sign codes in RAM, fixed-size adjacency records on disk.
    signs = np.packbits(matrix >= 0, axis=1)
    query_bits = np.packbits(q >= 0)
    links = np.full((len(matrix), 6), -1, dtype="<i4")
    for row, neighbors in graph.layers[0].items():
        links[row, : len(neighbors)] = neighbors
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "links.bin"
        links.tofile(path)
        seen = set()
        frontier = {graph.entry}
        with path.open("rb") as file:
            while frontier and len(seen) < 40:
                batch = sorted(
                    frontier, key=lambda i: int(np.bitwise_count(signs[i] ^ query_bits).sum())
                )[: min(4, 40 - len(seen))]
                for row in batch:
                    file.seek(row * links.strides[0])
                    neighbors = np.frombuffer(file.read(24), dtype="<i4")
                    seen.add(row)
                    frontier.update(int(n) for n in neighbors if n >= 0)
                frontier -= seen
        candidates = sorted(seen, key=lambda r: -float(matrix[r] @ q))[:10]
        exact = set(np.argsort(-(matrix @ q))[:10].tolist())
        # Estimate object bytes if each touched fragment had to be fetched whole.
        layouts = {}
        for per_fragment in [8, 64]:
            blocks = {row // per_fragment for row in seen}
            fetched = sum(min(per_fragment, len(matrix) - b * per_fragment) * 24 for b in blocks)
            layouts[str(per_fragment)] = {
                "fragments": len(blocks),
                "modeled_bytes": fetched,
                "useful_adjacency_bytes": len(seen) * 24,
            }
        result = {
            "products": len(products),
            "read_budget": 40,
            "actual_reads": len(seen),
            "fixed_record_bytes": 24,
            "recall_at_10": len(exact.intersection(candidates)) / 10,
            "final_ids": products.iloc[candidates].id.tolist(),
            "object_layout_estimates": layouts,
        }
    print(result)
    evidence("page-reads", result, tier=2)


if __name__ == "__main__":
    main()
