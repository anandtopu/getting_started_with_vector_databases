"""Evaluate a native LanceDB result against the same judgments.

Concepts: unindexed exact scan, cosine distance, relevance versus neighbors.
Run: uv run --extra embedded python modules/04_benchmarking/examples/02_production.py
Expected: LanceDB result quality and exact neighbor recall recorded
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

# course-extra: embedded
import time
import uuid

import lancedb

from common.bench.ground_truth import neighbor_reference
from common.bench.metrics import ndcg_at_k, precision_at_k, reciprocal_rank, tie_aware_recall
from common.data import search_queries
from common.pretty import show_hits
from common.settings import cache_dir
from common.teaching import catalog, evidence, ranked_hits


def main() -> None:
    products, vectors, query, _ = catalog(1000)
    path = cache_dir() / "tier1" / ("lance-" + uuid.uuid4().hex)
    db = lancedb.connect(str(path))
    try:
        table = db.create_table(
            "products",
            data=[
                {"id": key, "vector": v.tolist()}
                for key, v in zip(products["id"], vectors, strict=True)
            ],
        )
        start = time.perf_counter()
        rows = table.search(query).distance_type("cosine").limit(10).to_list()
        elapsed = (time.perf_counter() - start) * 1000
        ids = [row["id"] for row in rows]
        truth = neighbor_reference(
            vectors, products["id"].tolist(), products.to_dict("records"), query, 10, "cosine"
        )
        judgments = {
            key: grade
            for key, grade in search_queries()[0]["qrels"].items()
            if key in set(products["id"])
        }
        metrics = {
            "recall": tie_aware_recall(ids, truth, 10),
            "precision": precision_at_k(ids, judgments, 10),
            "mrr": reciprocal_rank(ids, judgments),
            "ndcg": ndcg_at_k(ids, judgments, 10),
            "retrieval_ms": elapsed,
        }
        # KEY IDEA: no ANN index was built; poor relevance cannot be blamed on approximate retrieval here.
        show_hits(
            ranked_hits(products, [(r["id"], 1 - r["_distance"]) for r in rows]),
            elapsed,
            title="LanceDB judged query",
        )
        print(metrics)
        evidence("lancedb_quality", metrics)
    finally:
        db.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
