"""Query a self-provided Weaviate vector and change the hybrid weight.

Run: uv run --extra weaviate python modules/14_weaviate/examples/02_production.py
Concepts: Query a self-provided Weaviate vector and change the hybrid weight.
Expected: native near-vector filter and alpha sweep.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the weaviate profile first.
"""

# course-extra: weaviate
# course-profile: weaviate
from weaviate.classes.query import Filter, MetadataQuery

from common.tier3 import session


def main() -> None:
    # KEY IDEA: Query a self-provided Weaviate vector and change the hybrid weight.
    with session("weaviate", 160) as (store, rows, q):
        term = rows.iloc[0].sku
        key = next(iter(store.catalog))
        by_id = store.table.query.near_vector(
            q.tolist(),
            filters=Filter.by_id().equal(key),
            limit=1,
            return_metadata=MetadataQuery(distance=True),
        )
        assert str(by_id.objects[0].uuid) == key
        for alpha in (0.0, 0.5, 1.0):
            ranked = store.table.query.hybrid(
                query=term,
                vector=q.tolist(),
                alpha=alpha,
                query_properties=["body"],
                limit=5,
                return_metadata=MetadataQuery(score=True),
            )
            print("alpha", alpha, [(str(o.uuid), o.metadata.score) for o in ranked.objects])
            assert ranked.objects


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "weaviate")
