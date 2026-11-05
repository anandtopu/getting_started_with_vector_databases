"""Persist vectors, metadata and stable IDs as a complete snapshot.

Run: uv run python modules/03_tinyvec/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/03_tinyvec/solutions/03_stretch.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import tempfile
from pathlib import Path

import numpy as np

from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


def solve(records: list[Record], path: Path) -> list[Record]:
    # KEY IDEA: this reference implements the stated acceptance policy.
    store = TinyVec()
    store.create_collection(CollectionSpec("exercise", 2, "cosine", "hand-v1"))
    try:
        store.upsert(records)
        store.save(path)
        restored = TinyVec.load(path)
        try:
            return restored.records()
        finally:
            restored.close()
    finally:
        store.close()


def main() -> None:
    with tempfile.TemporaryDirectory() as folder:
        print(solve([Record("mug", np.array([1.0, 0.2]), {"price": 20})], Path(folder)))


if __name__ == "__main__":
    main()
