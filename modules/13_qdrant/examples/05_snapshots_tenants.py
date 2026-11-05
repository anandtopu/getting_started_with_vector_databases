"""Restore a real Qdrant snapshot to a new isolated collection.

Run: uv run --extra qdrant python modules/13_qdrant/examples/05_snapshots_tenants.py
Concepts: Restore a real Qdrant snapshot to a new isolated collection.
Expected: restored native snapshot IDs.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the qdrant profile first.
"""

# course-extra: qdrant
# course-profile: qdrant
import uuid

import httpx

from common.settings import setting
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Restore a real Qdrant snapshot to a new isolated collection.
    with (
        session("qdrant", 80) as (store, _, q),
        httpx.Client(base_url=setting("QDRANT_URL", "http://127.0.0.1:6333"), timeout=60) as http,
    ):
        expected = store._query(q, None, 3)
        snap = store.db.create_snapshot(store.name)
        target = "marlowe_restore_" + uuid.uuid4().hex
        try:
            blob = (
                http.get(f"/collections/{store.name}/snapshots/{snap.name}")
                .raise_for_status()
                .content
            )
            response = http.post(
                f"/collections/{target}/snapshots/upload",
                params={"priority": "snapshot", "wait": "true"},
                files={"snapshot": (snap.name, blob, "application/octet-stream")},
            )
            response.raise_for_status()
            pts = store.db.query_points(target, query=q.tolist(), using="dense", limit=3).points
            assert [p.id for p in pts] == [key for key, _ in expected]
            print("snapshot bytes", len(blob), "restored", len(pts))
        finally:
            if store.db.collection_exists(target):
                store.db.delete_collection(target)
            store.db.delete_snapshot(store.name, snap.name)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "qdrant")
