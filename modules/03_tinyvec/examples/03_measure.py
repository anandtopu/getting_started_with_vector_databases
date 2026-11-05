"""Show why filtering only the first few hits can lose valid results.

Concepts: prefilter, postfilter, candidate budget, filter recall.
Run: uv run python modules/03_tinyvec/examples/03_measure.py
Expected: postfilter returns 0; prefilter returns 1
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import numpy as np

from common.stores.registry import make_store
from common.stores.types import CollectionSpec, Record
from common.teaching import evidence, timed


def main() -> None:
    store = make_store()
    store.create_collection(CollectionSpec("filter-demo", 2, "cosine", "hand-v1"))
    rows = [
        Record("warmer-unavailable", np.array([1.0, 0.0]), {"stock": 0}),
        Record("warmer-available", np.array([0.9, 0.1]), {"stock": 4}),
    ]
    store.upsert(rows)
    expression = {"op": "gt", "field": "stock", "value": 0}
    try:
        post = [h for h in store.search([1, 0], 1) if h.metadata["stock"] > 0]
        pre = store.search([1, 0], 1, expression)
        assert not post and [h.id for h in pre] == ["warmer-available"]
        # KEY IDEA: eligibility is part of the nearest-neighbor question.
        evidence(
            "filter_order",
            {
                "postfilter_count": len(post),
                "prefilter_count": len(pre),
                "prefilter": timed(lambda: store.search([1, 0], 1, expression)),
            },
        )
        print("postfilter returns 0; prefilter returns 1")
    finally:
        store.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
