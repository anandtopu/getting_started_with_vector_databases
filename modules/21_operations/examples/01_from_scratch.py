"""Bound retries and compact versioned rows.
Run: uv run python modules/21_operations/examples/01_from_scratch.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""

from common.ops.ingestion import ingest, stable_id
from tinyvec.storage import VersionedRows


def main():
    store = VersionedRows()

    def write(batch):
        for key, value in batch:
            store.upsert(key, value)

    rows = [(stable_id("seller-a", str(i)), {"price": i}) for i in range(100)]
    first = ingest(rows, write, batch_size=16, pending_limit=2)
    ingest(rows, write, batch_size=16)
    assert len(store.live()) == 100 and len(store.rows) == 200
    for key, _ in rows[:10]:
        store.delete(key)
    live = store.live()
    print(first, store.compact())
    assert store.live() == live and len(live) == 90
    assert stable_id("seller-b", "0") != stable_id("seller-a", "0")
    print("Replay preserves identity; deletion hides rows before reclamation.")


if __name__ == "__main__":
    main()
