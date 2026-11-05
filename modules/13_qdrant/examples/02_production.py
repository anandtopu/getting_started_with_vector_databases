"""Configure a Qdrant payload index and quantized dense search.

Run: uv run --extra qdrant python modules/13_qdrant/examples/02_production.py
Concepts: Configure a Qdrant payload index and quantized dense search.
Expected: native payload index and quantized search.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the qdrant profile first.
"""

# course-extra: qdrant
# course-profile: qdrant
from qdrant_client import models as m

from common.tier3 import session


def main() -> None:
    # KEY IDEA: Configure a Qdrant payload index and quantized dense search.
    with session("qdrant", quantize=True) as (store, _, q):
        store.db.create_payload_index(
            store.name, "region", field_schema=m.PayloadSchemaType.KEYWORD, wait=True
        )
        filt = m.Filter(must=[m.FieldCondition(key="region", match=m.MatchValue(value="north"))])
        points = store.db.query_points(
            store.name,
            query=q.tolist(),
            using="dense",
            query_filter=filt,
            limit=5,
            with_payload=True,
            search_params=m.SearchParams(
                quantization=m.QuantizationSearchParams(rescore=True, oversampling=2)
            ),
        ).points
        assert points and all(p.payload["region"] == "north" for p in points)
        print(
            "north region",
            [p.id for p in points],
            store.db.get_collection(store.name).payload_schema,
        )


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "qdrant")
