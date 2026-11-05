"""Measure read-after-write visibility under three Milvus policies.

Run: uv run --extra milvus python modules/15_milvus/examples/05_partitions_consistency.py
Concepts: Measure read-after-write visibility under three Milvus policies.
Expected: partition and consistency observations.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the milvus profile first.
"""

# course-extra: milvus
# course-profile: milvus
import time

from pymilvus import DataType

from common.stores.milvus import MilvusStore
from common.teaching import evidence


def main() -> None:
    # KEY IDEA: Measure read-after-write visibility under three Milvus policies.
    adapter = MilvusStore()
    db = adapter.db
    name = adapter.name
    schema = db.create_schema(auto_id=False)
    schema.add_field("id", DataType.INT64, is_primary=True)
    schema.add_field("tenant", DataType.VARCHAR, max_length=40, is_partition_key=True)
    schema.add_field("v", DataType.FLOAT_VECTOR, dim=2)
    idx = db.prepare_index_params()
    idx.add_index(field_name="v", index_type="FLAT", metric_type="COSINE")
    db.create_collection(name, schema=schema, index_params=idx, num_partitions=4)
    try:
        db.insert(
            name,
            [
                {"id": 1, "tenant": "north", "v": [1.0, 0.0]},
                {"id": 2, "tenant": "south", "v": [0.0, 1.0]},
            ],
        )
        seen = {}
        for policy in ["Eventually", "Session", "Strong"]:
            start = time.perf_counter()
            rows = db.query(
                name,
                filter='tenant == "north"',
                output_fields=["id", "tenant"],
                consistency_level=policy,
            )
            seen[policy] = {
                "ids": [r["id"] for r in rows],
                "milliseconds": 1000 * (time.perf_counter() - start),
            }
        assert seen["Strong"]["ids"] == [1]
        print(seen, db.list_partitions(name))
        evidence("milvus-consistency", {"observations": seen}, tier=3)
    finally:
        db.drop_collection(name)
        db.close()


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "milvus")
