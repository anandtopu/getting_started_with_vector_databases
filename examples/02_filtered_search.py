"""Restrict semantic search to affordable, available products in a chosen region.

Run: uv run python examples/02_filtered_search.py
Expected: returned rows have price < 100, stock > 0 and region north.
CPU: about 2 seconds. Needs: committed semantic vectors and core packages.
No network, downloaded model, or Docker.
"""

from common.apps.search import open_catalog, search_saved
from common.errors import run_cli
from common.pretty import show_hits


def main() -> None:
    store, _, _ = open_catalog()
    try:
        query, hits, elapsed = search_saved(store, "q014")
        print(query["text"])
        # KEY IDEA: restrict eligible records before selecting the nearest neighbors.
        assert all(
            hit.metadata["price"] < 100
            and hit.metadata["stock"] > 0
            and hit.metadata["region"] == "north"
            for hit in hits
        )
        show_hits(hits, elapsed, title="Filtered Marlowe Search")
    finally:
        store.close()


if __name__ == "__main__":
    run_cli(main)
