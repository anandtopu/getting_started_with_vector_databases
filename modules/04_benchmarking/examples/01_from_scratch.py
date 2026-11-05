"""Compute retrieval metrics from their definitions.

Concepts: neighbor recall, precision, reciprocal rank, graded nDCG.
Run: uv run python modules/04_benchmarking/examples/01_from_scratch.py
Expected: recall 0.5, precision 0.5, MRR 0.5
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.bench.metrics import (
    latency_summary,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def main() -> None:
    found = ["flask", "warmer"]
    exact = ["warmer", "chair"]
    judgments = {"warmer": 3, "lamp": 1}
    # KEY IDEA: exact neighbors and useful answers are two different reference sets.
    print("recall:", recall_at_k(found, exact, 2))
    print("precision:", precision_at_k(found, judgments, 2))
    print("MRR:", reciprocal_rank(found, judgments))
    print("nDCG:", round(ndcg_at_k(found, judgments, 2), 4))
    print("latency:", latency_summary([1.0, 2.0, 3.0, 4.0, 100.0]))
    assert (
        recall_at_k(found, exact, 2)
        == precision_at_k(found, judgments, 2)
        == reciprocal_rank(found, judgments)
        == 0.5
    )
    print("Open common/bench/metrics.py: each implementation directly follows its definition.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
