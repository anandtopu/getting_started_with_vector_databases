"""Retrieve sparse product matches using bm25s.

Concepts: Retrieve sparse product matches using bm25s.
Run: uv run --extra libs python modules/10_filtering_hybrid/examples/02_production.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: libs
import bm25s

from common.data import product_texts
from common.teaching import catalog


def main():
    products, _, _, _ = catalog(200)
    corpus = product_texts(products)
    engine = bm25s.BM25()
    engine.index(bm25s.tokenize(corpus, show_progress=False), show_progress=False)
    rows, scores = engine.retrieve(
        bm25s.tokenize(["waterproof hiking boots"], show_progress=False), k=5, show_progress=False
    )
    print(list(zip(products.iloc[rows[0]].title, scores[0].tolist(), strict=True)))
    assert scores[0][0] > 0


if __name__ == "__main__":
    main()
