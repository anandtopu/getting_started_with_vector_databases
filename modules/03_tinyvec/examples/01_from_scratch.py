"""Walk through TinyVec storage and mutation.

Concepts: stable IDs, replacement, deletion, exact scoring.
Run: uv run python modules/03_tinyvec/examples/01_from_scratch.py
Expected: same ID updated once; deleted ID absent
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import time

import numpy as np

from common.pretty import show_hits
from common.stores.registry import make_store
from common.stores.types import CollectionSpec, Record


def main() -> None:
    store = make_store("tinyvec")
    store.create_collection(CollectionSpec("desk", 2, "cosine", "hand-v1"))
    try:
        store.insert(
            [
                Record(
                    "warmer",
                    np.array([1, 0.1]),
                    {"title": "Ceramic mug warmer", "price": 30, "region": "north"},
                )
            ]
        )
        # KEY IDEA: upsert replaces the whole record for the same ID; it does not append another copy.
        store.upsert(
            [
                Record(
                    "warmer",
                    np.array([1, 0.1]),
                    {"title": "Ceramic mug warmer", "price": 25, "region": "north"},
                )
            ]
        )
        start = time.perf_counter()
        hits = store.search([1, 0], space="hand-v1")
        elapsed = (time.perf_counter() - start) * 1000
        assert len(hits) == 1 and hits[0].metadata["price"] == 25
        show_hits(hits, elapsed, title="Updated product")
        store.delete(["warmer"])
        assert store.search([1, 0]) == []
        print("Deleted ID absent; empty search is valid.")
    finally:
        store.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
