"""Use dense, sparse and multiple vectors through the Qdrant Query API.

Run: uv run --extra qdrant python modules/13_qdrant/examples/04_hybrid_multivector.py
Concepts: Use dense, sparse and multiple vectors through the Qdrant Query API.
Expected: named-vector fusion and MaxSim.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the qdrant profile first.
"""

# course-extra: qdrant
# course-profile: qdrant
import uuid
from contextlib import closing

from qdrant_client import QdrantClient
from qdrant_client import models as m

from common.settings import setting
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Use dense, sparse and multiple vectors through the Qdrant Query API.
    with session("qdrant") as (store, rows, q):
        hits = store.hybrid_search(rows.iloc[0].sku, q, 5)
        print("fused named fields", [h.id for h in hits])
    with closing(QdrantClient(url=setting("QDRANT_URL", "http://127.0.0.1:6333"))) as db:
        name = "marlowe_" + uuid.uuid4().hex
        db.create_collection(
            name,
            vectors_config={
                "tokens": m.VectorParams(
                    size=2,
                    distance=m.Distance.COSINE,
                    multivector_config=m.MultiVectorConfig(
                        comparator=m.MultiVectorComparator.MAX_SIM
                    ),
                )
            },
        )
        try:
            db.upsert(
                name,
                points=[
                    m.PointStruct(id=1, vector={"tokens": [[1.0, 0.0], [0.0, 1.0]]}),
                    m.PointStruct(id=2, vector={"tokens": [[1.0, 0.0]]}),
                ],
                wait=True,
            )
            points = db.query_points(name, query=[[1.0, 0.0], [0.0, 1.0]], using="tokens").points
            assert points[0].id == 1
            print("two-token coverage", [(p.id, p.score) for p in points])
        finally:
            db.delete_collection(name)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "qdrant")
