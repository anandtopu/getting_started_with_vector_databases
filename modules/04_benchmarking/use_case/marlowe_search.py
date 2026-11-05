"""Judge a faster but wrong search policy.

Concepts: latency-quality trade-off, exact baseline versus relevance.
Run: uv run python modules/04_benchmarking/use_case/marlowe_search.py
Expected: fast first-five policy has worse useful-hit rate
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.bench.metrics import precision_at_k
from common.data import search_queries
from common.teaching import catalog, evidence, timed
from tinyvec.exact import exact_knn


def main() -> None:
    products, vectors, query, _ = catalog(1000)
    ids = products["id"].tolist()
    qrels = search_queries()[0]["qrels"]

    def exact() -> list[str]:
        return [key for key, _ in exact_knn(vectors, query, ids, 5)]

    def naive() -> list[str]:
        return ids[:5]

    quality = {
        name: precision_at_k(call(), qrels, 5)
        for name, call in [("exact", exact), ("first_five", naive)]
    }
    assert quality["exact"] > quality["first_five"]
    evidence(
        "quality_tradeoff",
        {"precision_at_5": quality, "exact": timed(exact), "first_five": timed(naive)},
    )
    print(quality, "Product decision: reject the faster policy because it ignores the request.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
