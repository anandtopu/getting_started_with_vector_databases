"""TinyVec 1.0 reference: mutable HNSW/PQ, scoped filters and portable snapshots.
Run: uv run --extra libs python capstones/01_tinyvec/solution/project.py --evaluate
Expected: mutation/restore check, then three comparable benchmark records. CPU: minutes.
Needs: included MiniLM vectors; optional FAISS comparison; no network or server.
"""

import argparse
import tempfile
from pathlib import Path

import numpy as np

from common.bench.config import BenchConfig
from common.bench.leaderboard import write_leaderboard
from common.bench.runner import run_benchmark
from common.errors import run_cli
from common.settings import ROOT
from common.stores.ann import IndexedTinyVec
from common.stores.types import CollectionSpec, Record


def build(kind, records, spec):
    if kind not in {"hnsw", "pq"}:
        raise ValueError("Choose hnsw or pq")
    options = (
        {"M": 8, "efConstruction": 60, "efSearch": 60}
        if kind == "hnsw"
        else {"parts": 4, "centroids": 16}
    )
    store = IndexedTinyVec(kind=kind, oversample=16, **options)
    store.create_collection(spec)
    store.upsert(records)
    store.build()
    return store


def restore(path):
    return IndexedTinyVec.load(path)


def evaluate():
    results = []
    for backend, parameters in [
        ("ann", {"kind": "hnsw", "M": 12, "efConstruction": 80, "efSearch": 80}),
        ("ann", {"kind": "pq", "parts": 16, "centroids": 16, "oversample": 32}),
        ("faiss-flat", {}),
    ]:
        kind = parameters.get("kind", backend)
        config = BenchConfig(
            name="capstone-tinyvec-" + kind,
            backend=backend,
            parameters=parameters,
            dataset="catalog",
            limit=500,
            k=10,
            warmup=5,
            repetitions=3,
            queries=30,
            split="test",
        )
        report = run_benchmark(config, ROOT / "results")
        results.append({"kind": kind, "run_id": report["run_id"], "summary": report["summary"]})
    write_leaderboard(ROOT / "results")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluate", action="store_true")
    args = parser.parse_args()
    vectors = np.random.default_rng(42).normal(size=(200, 16)).astype(np.float32)
    rows = [
        Record(str(i), v, {"seller_id": "a" if i % 2 == 0 else "b"}) for i, v in enumerate(vectors)
    ]
    for kind in ["hnsw", "pq"]:
        store = build(kind, rows, CollectionSpec("capstone", 16))
        store.delete(["0"])
        with tempfile.TemporaryDirectory() as folder:
            store.save(Path(folder))
            loaded = restore(Path(folder))
            found = loaded.search(vectors[0], 10, {"op": "eq", "field": "seller_id", "value": "a"})
            assert all(h.metadata["seller_id"] == "a" and h.id != "0" for h in found)
            loaded.close()
        store.close()
    print("HNSW/PQ mutation, filter and restore checks passed")
    if args.evaluate:
        print(evaluate())


if __name__ == "__main__":
    run_cli(main)
