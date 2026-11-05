"""Save and reload TinyVec without pickle, then verify unchanged neighbors.

Run: uv run python examples/03_persistence.py
Expected: Snapshot round trip preserved 5 neighbors.
CPU: about 2 seconds. Needs: committed catalog; uses and removes a temporary snapshot.
No model, network, or Docker.
"""

import tempfile
from pathlib import Path

from common.apps.search import open_catalog, search_saved
from common.errors import run_cli
from common.settings import cache_dir
from tinyvec import TinyVec


def main() -> None:
    store, _, _ = open_catalog(limit=1000)
    cache_dir().mkdir(parents=True, exist_ok=True)
    try:
        _, before, _ = search_saved(store)
        with tempfile.TemporaryDirectory(dir=cache_dir()) as directory:
            store.save(Path(directory))
            restored = TinyVec.load(Path(directory))
            try:
                _, after, _ = search_saved(restored)
                # KEY IDEA: IDs and embedding-space metadata survive the round trip.
                assert [h.id for h in before] == [h.id for h in after]
            finally:
                restored.close()
        print(f"Snapshot round trip preserved {len(before)} neighbors.")
    finally:
        store.close()


if __name__ == "__main__":
    run_cli(main)
