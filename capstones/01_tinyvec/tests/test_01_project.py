"""Reference acceptance; the same verify function accepts a learner project module."""

from pathlib import Path

import numpy as np

from common.exercise_checks import load
from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


def verify(project, tmp_path):
    vectors = np.random.default_rng(3).normal(size=(100, 16)).astype(np.float32)
    records = [Record(str(i), v, {"tenant": "a" if i % 2 else "b"}) for i, v in enumerate(vectors)]
    spec = CollectionSpec("capstone", 16)
    exact = TinyVec()
    exact.create_collection(spec)
    exact.upsert(records)
    for kind in ["hnsw", "pq"]:
        store = project.build(kind, records, spec)
        assert store.kind == kind
        truth = {h.id for h in exact.search(vectors[2], 10)}
        assert len(truth & {h.id for h in store.search(vectors[2], 10)}) / 10 >= 0.8
        store.delete(["2"])
        path = tmp_path / kind
        store.save(path)
        loaded = project.restore(path)
        hits = loaded.search(vectors[2], 10, {"op": "eq", "field": "tenant", "value": "b"})
        assert hits and all(h.id != "2" and h.metadata["tenant"] == "b" for h in hits)
        loaded.close()
        store.close()


def test_capstone_01(tmp_path):
    root = Path(__file__).resolve().parents[1]
    load(root / "starter/project.py").main()
    verify(load(root / "solution/project.py"), tmp_path)
