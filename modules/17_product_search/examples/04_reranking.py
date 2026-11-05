"""Observe candidate reranking and protect an exact identifier.

Run: uv run --extra models python modules/17_product_search/examples/04_reranking.py
Expected: query/document scores and an exact SKU pinned first.
CPU: seconds to one minute. Needs: models extra, cached cross encoder. No implicit downloads.
"""
# course-extra: models

from common.apps.database import AppDatabase
from common.apps.product_search import ProductSearch
from common.embeddings import Reranker, frozen_query
from common.pretty import show_hits
from common.settings import data_dir


def main() -> None:
    vector, _ = frozen_query("q001", data_dir())
    with AppDatabase() as db:
        search = ProductSearch(db, 100)
        # KEY IDEA: a cross encoder cannot recover a document absent from candidates.
        result = search.search("MM-11-0000031", vector, k=5, reranker=Reranker())
        show_hits(
            result.hits, sum(result.timings_ms.values()), title="Reranking with identifier policy"
        )
        assert result.hits[0].metadata["sku"] == "MM-11-0000031"


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
