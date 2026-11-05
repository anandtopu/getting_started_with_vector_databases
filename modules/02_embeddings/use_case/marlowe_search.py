"""Build a first semantic search with NumPy.

Concepts: frozen real embeddings, exact retrieval, no database.
Run: uv run python modules/02_embeddings/use_case/marlowe_search.py
Expected: five mug warmers with scores and timing
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import time

from common.pretty import show_hits
from common.teaching import catalog, ranked_hits
from tinyvec.exact import exact_knn


def main() -> None:
    products, vectors, query, _ = catalog(1000)
    start = time.perf_counter()
    ranked = exact_knn(vectors, query, products["id"].tolist(), 5)
    show_hits(
        ranked_hits(products, ranked),
        (time.perf_counter() - start) * 1000,
        title="Marlowe Search v1: NumPy",
    )
    print(
        "Product decision: 1k items need no server; arbitrary text needs a matching cached model."
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
