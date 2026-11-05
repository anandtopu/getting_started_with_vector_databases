"""Measure strict filtering and score a second-stage ranking.

Concepts: Measure strict filtering and score a second-stage ranking.
Run: uv run python modules/10_filtering_hybrid/examples/03_measure.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

import json

from common.bench.metrics import ndcg_at_k
from common.data import search_queries
from common.index_lessons import trial
from common.settings import ROOT
from common.teaching import evidence


def main():
    ranking = json.loads((ROOT / "data/tier2/reranking.json").read_text())
    judged = next(q for q in search_queries() if q["id"] == ranking["query_id"])
    after = sorted(ranking["candidates"], key=lambda r: -r["score"])
    observations = {
        "filter": [
            trial(
                "hnsw",
                expression={"op": "eq", "field": "region", "value": "north"},
                filter_policy=p,
                oversample=1,
            )
            for p in ("post", "traverse", "adaptive")
        ],
        "cross_encoder": after,
        "before": [r["id"] for r in ranking["candidates"]],
        "ndcg_before": ndcg_at_k([r["id"] for r in ranking["candidates"]], judged["qrels"], 10),
        "ndcg_after": ndcg_at_k([r["id"] for r in after], judged["qrels"], 10),
    }
    print(observations)
    evidence("lesson-10_filtering_hybrid", {"observations": observations}, tier=2)


if __name__ == "__main__":
    main()
