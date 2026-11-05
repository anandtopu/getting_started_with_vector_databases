"""Model logical backup as a reproducible catalog export.

Run: uv run python modules/11_embedded/examples/01_from_scratch.py
Concepts: Model logical backup as a reproducible catalog export.
Expected: original ranked IDs after restore.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

import tempfile
from pathlib import Path

from common.data import records_from_products
from common.stores.types import CollectionSpec
from common.teaching import catalog
from tinyvec import TinyVec


def main() -> None:
    # KEY IDEA: Model logical backup as a reproducible catalog export.
    products, matrix, q, meta = catalog(80)
    store = TinyVec()
    store.create_collection(CollectionSpec("tiny", matrix.shape[1], "cosine", meta["space"]))
    store.upsert(records_from_products(products, matrix))
    with tempfile.TemporaryDirectory() as tmp:
        store.save(Path(tmp))
        before = store.search(q, 3)
        store.delete([before[0].id])
        restored = TinyVec.load(Path(tmp)).search(q, 3)
        assert [h.id for h in before] == [h.id for h in restored]
        print("restored IDs", [h.id for h in restored])


if __name__ == "__main__":
    main()
