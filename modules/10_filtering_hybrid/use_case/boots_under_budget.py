"""Retrieve waterproof hiking boots in stock in the buyer's region.

Concepts: Retrieve waterproof hiking boots in stock in the buyer's region.
Run: uv run python modules/10_filtering_hybrid/use_case/boots_under_budget.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.apps.search import open_catalog
from common.data import search_queries
from common.embeddings import frozen_query
from common.settings import data_dir


def main():
    query = next(
        q for q in search_queries() if "boot" in q["text"].lower() and q["type"] == "filtered"
    )
    store, _, _ = open_catalog("ann", 1000, kind="ivf", nprobe=8)
    try:
        vector, meta = frozen_query(query["id"], data_dir())
        hits = store.hybrid_search(query["text"], vector, 5, query["filter"], space=meta["space"])
        print(query["text"], [(h.id, h.metadata["title"], h.metadata["price"]) for h in hits])
        assert hits and all(
            h.metadata["price"] < 100
            and h.metadata["stock"] > 0
            and h.metadata["region"] == "north"
            for h in hits
        )
    finally:
        store.close()


if __name__ == "__main__":
    main()
