"""Flush real catalog vectors and inspect native DISKANN build state.

Run: uv run --extra milvus python modules/15_milvus/examples/06_disk_index.py
Concepts: Flush real catalog vectors and inspect native DISKANN build state.
Expected: 4,096 indexed disk rows.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the milvus profile first.
"""

# course-extra: milvus
# course-profile: milvus
import time

from common.teaching import evidence
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Flush real catalog vectors and inspect native DISKANN build state.
    with session("milvus", 4096, index="DISKANN") as (s, _, q):
        name = next(
            n
            for n in s.db.list_indexes(s.name)
            if s.db.describe_index(s.name, n)["field_name"] == "v"
        )
        deadline = time.monotonic() + 150
        while True:
            info = dict(s.db.describe_index(s.name, name))
            if info.get("indexed_rows", 0) >= 4096:
                break
            if time.monotonic() > deadline:
                raise TimeoutError(f"DISKANN did not finish indexing 4096 sealed rows: {info}")
            time.sleep(1)
        s.db.refresh_load(s.name)
        hits = s.search(q, 5)
        assert info["index_type"] == "DISKANN" and hits
        print("server index statistics", info, "top IDs", [h.id for h in hits])
        evidence("milvus-diskann", {"status": info, "ids": [h.id for h in hits]}, tier=3)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "milvus")
