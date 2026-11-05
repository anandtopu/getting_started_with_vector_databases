"""Create an indexed Milvus collection and search named fields.

Run: uv run --extra milvus python modules/15_milvus/examples/02_production.py
Concepts: Create an indexed Milvus collection and search named fields.
Expected: IVF collection and native result.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the milvus profile first.
"""

# course-extra: milvus
# course-profile: milvus
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Create an indexed Milvus collection and search named fields.
    with session("milvus", 160, index="IVF_FLAT") as (s, _, q):
        hits = s.db.search(
            collection_name=s.name,
            data=[q.tolist()],
            anns_field="v",
            limit=5,
            search_params={"metric_type": "COSINE", "params": {"nprobe": 8}},
            output_fields=["body"],
        )
        print(
            "schema",
            s.db.describe_collection(s.name)["collection_name"],
            "indexes",
            s.db.list_indexes(s.name),
        )
        print("first hit", hits[0][0])
        assert len(hits[0]) == 5


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "milvus")
