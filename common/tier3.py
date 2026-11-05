"""Small shared catalog sessions and measured Tier 3 drills."""

import tempfile
from contextlib import contextmanager
from pathlib import Path

from common.bench.config import load_config
from common.bench.runner import run_benchmark
from common.data import records_from_products
from common.settings import ROOT, cache_dir
from common.stores.registry import make_store
from common.stores.types import CollectionSpec
from common.teaching import catalog, evidence


@contextmanager
def session(backend, count=160, **parameters):
    products, matrix, query, meta = catalog(count)
    cache = cache_dir() / "tier3"
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as working:
        path = cache / "chroma" if backend == "chroma" else Path(working) / "db"
        store = make_store(backend, path=path, **parameters)
        try:
            store.create_collection(
                CollectionSpec("catalog", matrix.shape[1], "cosine", meta["space"])
            )
            store.upsert(records_from_products(products, matrix))
            if hasattr(store, "build"):
                store.build()
            yield store, products, query
        finally:
            store.close()


def restore_drill(backend):
    with tempfile.TemporaryDirectory() as temp, session(backend) as (source, _, q):
        backup = Path(temp) / "snapshot"
        expected = [h.id for h in source.search(q, 5)]
        source.save(backup)
        source.delete(expected[:1])
        assert expected[0] not in [h.id for h in source.search(q, 5)]
        dst = make_store(
            backend,
            path=cache_dir() / "tier3/chroma" if backend == "chroma" else Path(temp) / "restore-db",
        )
        try:
            dst.restore(backup)
            after = [h.id for h in dst.search(q, 5)]
            if after != expected:
                raise AssertionError((expected, after))
        finally:
            dst.close()
    return {
        "backend": backend,
        "deleted": expected[0],
        "restored": after,
        "snapshot": "logical reimport into a newly created collection",
    }


def measure(backend, **updates):
    config = load_config(ROOT / "configs/bench/tier3" / f"{backend}.yaml").model_copy(
        update={
            "name": f"lesson-{backend}",
            "limit": 200,
            "queries": 12,
            "warmup": 4,
            "repetitions": 3,
            **updates,
        }
    )
    run = run_benchmark(config, cache_dir() / "tier3/lesson-benchmarks")
    print(run["run_id"], run["summary"])
    return run


def observe(name, rows):
    print(rows)
    evidence(name, {"observations": rows, "seed": 20261104}, tier=3)
