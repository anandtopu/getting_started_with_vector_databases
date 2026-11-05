"""Motivate semantic product discovery.

Concepts: a need expressed without the product name.
Run: uv run python modules/00_setup/use_case/marlowe_search.py
Expected: five useful products
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.apps.search import open_catalog, search_saved
from common.pretty import show_hits


def main() -> None:
    store, _, _ = open_catalog(limit=1000)
    try:
        query, hits, elapsed = search_saved(store)
        show_hits(hits, elapsed, title=query["text"])
        assert all("mug warmer" in h.metadata["title"] for h in hits)
        print("Product decision: offer semantic search for needs; retain precise SKU lookup.")
    finally:
        store.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
