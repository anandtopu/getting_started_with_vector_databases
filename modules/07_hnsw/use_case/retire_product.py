"""Remove a retired listing and rebuild search routes.

Concepts: Remove a retired listing and rebuild search routes.
Run: uv run python modules/07_hnsw/use_case/retire_product.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.apps.search import open_catalog, search_saved


def main():
    store, _, _ = open_catalog("ann", 220, kind="hnsw", M=6, efConstruction=24)
    try:
        _, old, _ = search_saved(store)
        retired = old[0].id
        store.delete([retired])
        _, fresh, _ = search_saved(store)
        assert retired not in {h.id for h in fresh}
        print(
            "retired",
            retired,
            "new results",
            [h.id for h in fresh],
            "rebuilt graph bytes",
            store.index.payload_bytes,
        )
    finally:
        store.close()


if __name__ == "__main__":
    main()
