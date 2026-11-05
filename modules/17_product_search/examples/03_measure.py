"""Compare dense and hybrid SKU relevance on the same records.

Run: uv run  python modules/17_product_search/examples/03_measure.py
Expected: hybrid retrieves the literal SKU; timings and nDCG are recorded.
CPU: seconds to one minute. Needs: base, saved vectors. No implicit downloads.
"""

from common.apps.database import AppDatabase
from common.apps.product_search import ProductSearch
from common.bench.metrics import ndcg_at_k
from common.data import search_queries
from common.embeddings import frozen_query
from common.settings import data_dir
from common.teaching import evidence


def main() -> None:
    q = next(q for q in search_queries() if q["id"] == "q001")
    vector, _ = frozen_query(q["id"], data_dir())
    rows = {}
    with AppDatabase() as db:
        search = ProductSearch(db, 1000)
        for mode in ["dense", "hybrid", "lexical"]:
            result = search.search(q["text"], vector, mode=mode)
            ids = [h.id for h in result.hits]
            # KEY IDEA: relevance comes from independent judgments, not cosine scores.
            rows[mode] = {
                "ids": ids,
                "ndcg10": ndcg_at_k(ids, q["qrels"], 10),
                "timings_ms": result.timings_ms,
            }
    print(rows)
    evidence("product-ranking", rows, tier=4)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
