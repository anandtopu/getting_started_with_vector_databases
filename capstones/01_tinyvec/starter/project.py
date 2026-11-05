"""Runnable starting point for Capstone 01.
Run: uv run python capstones/01_tinyvec/starter/project.py
Expected: a working baseline, not completed acceptance. CPU: seconds.
Needs: included vectors; no downloads, credentials or containers.
"""

import numpy as np

from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


def build(kind, records, spec):
    # YOUR CODE HERE: replace the exact baseline with selectable HNSW/PQ and preserve snapshots.
    store = TinyVec()
    store.create_collection(spec)
    store.upsert(records)
    return store


def main() -> None:
    store = build("exact", [Record("a", np.array([1.0, 0.0]))], CollectionSpec("starter", 2))
    print([h.id for h in store.search([1, 0])])
    store.close()


if __name__ == "__main__":
    main()
