"""Serve available products and preserve them across a restart.

Concepts: metadata filtering, snapshot restore, IDs.
Run: uv run python modules/03_tinyvec/use_case/marlowe_search.py
Expected: same eligible IDs after restore
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import tempfile
from pathlib import Path

from common.apps.search import open_catalog, search_saved
from common.pretty import show_hits
from tinyvec import TinyVec


def main() -> None:
    store, _, _ = open_catalog(limit=1000)
    expression = {
        "op": "and",
        "clauses": [
            {"op": "gt", "field": "stock", "value": 0},
            {"op": "lte", "field": "price", "value": 30},
        ],
    }
    try:
        _, before, _ = search_saved(store, expression=expression)
        with tempfile.TemporaryDirectory() as folder:
            store.save(Path(folder))
            restored = TinyVec.load(Path(folder))
            try:
                _, after, elapsed = search_saved(restored, expression=expression)
                assert [h.id for h in before] == [h.id for h in after]
                show_hits(after, elapsed, title="Available products after restore")
            finally:
                restored.close()
        print(
            "Product decision: snapshot local experiments; do not promise transactional multiwriter service guarantees."
        )
    finally:
        store.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
