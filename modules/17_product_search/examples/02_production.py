"""Run filtered hybrid search in a real local Qdrant database.

Run: uv run --extra qdrant python modules/17_product_search/examples/02_production.py
Expected: five eligible products and native hybrid results.
CPU: seconds to one minute. Needs: qdrant extra, committed catalog. No implicit downloads.
"""
# course-extra: qdrant

from common.apps.database import AppDatabase
from common.apps.product_search import ProductSearch
from common.embeddings import frozen_query
from common.pretty import show_hits
from common.search.query_parser import parse_query
from common.settings import data_dir


def main() -> None:
    query, meta = frozen_query("q000", data_dir())
    text = "mug warmer under $100 in stock in the north region"
    with AppDatabase("qdrant-local") as db:
        search = ProductSearch(db, 500)
        result = search.search(text, query, k=5)
        show_hits(result.hits, result.timings_ms["retrieval"], title="Application BM25 + dense RRF")
        # KEY IDEA: native fusion and application fusion are separate implementations.
        native = search.store.hybrid_search(
            "mug warmer", query, 5, parse_query(text).filter, space=meta["space"]
        )
        show_hits(native, 0, title="Native Qdrant sparse-count + dense RRF (untimed)")
        assert all(h.metadata["price"] < 100 for h in native)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
