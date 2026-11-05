"""Measure cold computation and tenant-aware cached retrieval.
Run: uv run python modules/22_performance/examples/03_measure.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""

from common.ops.cache import QueryCache
from common.ops.drills import cache_measurement


def main():
    print(cache_measurement())
    cache = QueryCache()
    request = {"query": "chair", "filter": {"price": 100}, "k": 5}
    key = cache.key("a", "model-v1", 1, "search", request)
    cache.put(key, ["private-a"])
    variants = [
        cache.key("b", "model-v1", 1, "search", request),
        cache.key("a", "model-v2", 1, "search", request),
        cache.key("a", "model-v1", 2, "search", request),
        cache.key("a", "model-v1", 1, "search", {**request, "k": 10}),
    ]
    assert all(cache.get(k) is None for k in variants)
    print("Tenant, model, data generation and complete request change the key.")


if __name__ == "__main__":
    main()
