"""Measured local operations drills; synthetic policies are explicitly identified."""

import json
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

import numpy as np

from common.ops.backup import Backups
from common.ops.cache import QueryCache
from common.ops.ingestion import ingest, stable_id
from common.ops.migration import ModelRouter
from common.security.deletion import DeletionLedger
from common.stores.types import CollectionSpec, Record
from common.teaching import catalog
from tinyvec import TinyVec
from tinyvec.storage import VersionedRows


def operations():
    rows = VersionedRows()
    items = [(stable_id("seller-a", str(i)), i) for i in range(1000)]

    def write(batch):
        for key, value in batch:
            rows.upsert(key, value)

    first = ingest(items, write, batch_size=64, pending_limit=2)
    ingest(items, write, batch_size=64)
    assert len(rows.live()) == 1000
    for key, _ in items[:100]:
        rows.delete(key)
    before = rows.live()
    compacted = rows.compact()
    assert rows.live() == before and len(before) == 900
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "active.json"
        router = ModelRouter(path)
        router.publish("blue", "model-a", ready=True, measured_recall=1, minimum_recall=0.9)
        # Crash a separate process after atomic publication, then reload durable routing.
        code = "from pathlib import Path; import os; from common.ops.migration import ModelRouter; r=ModelRouter(Path(__import__('sys').argv[1])); r.publish('green','model-b',ready=True,measured_recall=1,minimum_recall=.9); os._exit(17)"
        child = subprocess.run([sys.executable, "-c", code, str(path)], check=False)
        recovered = ModelRouter(path)
        assert child.returncode == 17 and recovered.route("model-b") == "green"
        recovered.rollback()
        assert recovered.route("model-a") == "blue"
    return {
        "ingestion": first,
        "compaction": compacted,
        "migration_crash_exit": child.returncode,
        "rollback": "blue",
        "quality_scores": "fixture gate inputs, not measured relevance",
    }


def sqlite_compaction():
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "rows.db"
        with closing(sqlite3.connect(path)) as db:
            db.execute("CREATE TABLE versions(id INTEGER PRIMARY KEY, payload BLOB)")
            db.executemany(
                "INSERT INTO versions VALUES (?,?)", [(i, bytes(2048)) for i in range(2000)]
            )
            db.commit()
            before = path.stat().st_size
            db.execute("DELETE FROM versions WHERE id < 1500")
            db.commit()
            deleted = path.stat().st_size
            free = db.execute("PRAGMA freelist_count").fetchone()[0]
            started = time.perf_counter()
            db.execute("VACUUM")
            elapsed = time.perf_counter() - started
            after = path.stat().st_size
            assert db.execute("SELECT COUNT(*) FROM versions").fetchone()[0] == 500
            assert after < deleted
        return {
            "before_bytes": before,
            "after_delete_bytes": deleted,
            "after_vacuum_bytes": after,
            "free_pages_before": free,
            "vacuum_seconds": elapsed,
            "scope": "Native SQLite pages; not a vector-index rebuild benchmark",
        }


def disaster_recovery():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        store = TinyVec()
        store.create_collection(CollectionSpec("recovery", 2))
        store.upsert(
            [Record(str(i), np.array([1.0, i / 100]), {"seller_id": "a"}) for i in range(100)]
        )
        backups = Backups(root / "backups")
        name = backups.create(store, watermark=100)
        # Acknowledged after the backup: these writes are intentionally unrecoverable.
        store.upsert(
            [Record(str(i), np.array([1.0, 0]), {"seller_id": "a"}) for i in range(100, 105)]
        )
        ledger = DeletionLedger(root / "deletions.json")
        ledger.deny("a", ["0"])
        code = "from pathlib import Path; import json,sys; from common.ops.backup import Backups; from common.security.deletion import DeletionLedger; r=Path(sys.argv[1]); s,m=Backups(r/'backups').restore(sys.argv[2],DeletionLedger(r/'deletions.json')); print(json.dumps({'ids':[x.id for x in s.records()],'watermark':m['watermark']}))"
        start = time.perf_counter()
        child = subprocess.run(
            [sys.executable, "-c", code, str(root), name],
            check=True,
            capture_output=True,
            text=True,
        )
        elapsed = time.perf_counter() - start
        result = json.loads(child.stdout)
        assert len(result["ids"]) == 99 and "0" not in result["ids"]
        assert not set(map(str, range(100, 105))) & set(result["ids"])
        return {
            "restore_seconds_including_process_start": elapsed,
            "backup_watermark": 100,
            "last_acknowledged_watermark": 105,
            "lost_acknowledged_writes": 5,
            "resurrected_deletions": 0,
            "restored_rows": 99,
            "rpo_scope": "Five writes; no wall-clock RPO inferred",
            "ledger": "Survives separately from the data backup",
        }


def cache_measurement():
    _, vectors, query, _ = catalog(1000)
    cache = QueryCache()
    key = cache.key("a", "minilm", 0, "search", {"k": 10})

    def search():
        return np.argsort(-(vectors @ query), kind="stable")[:10].tolist()

    expected = search()
    cold, warm = [], []
    for _ in range(50):
        cache.clear()
        start = time.perf_counter()
        cache.put(key, search())
        cold.append((time.perf_counter() - start) * 1000)
        start = time.perf_counter()
        assert cache.get(key) == expected
        warm.append((time.perf_counter() - start) * 1000)
    assert cache.get(cache.key("b", "minilm", 0, "search", {"k": 10})) is None
    return {
        "samples": 50,
        "cold_p50_ms": float(np.median(cold)),
        "warm_p50_ms": float(np.median(warm)),
        "cold_p95_ms": float(np.percentile(cold, 95)),
        "warm_p95_ms": float(np.percentile(warm, 95)),
        "scope": "Exact kernel versus in-process cached ranking; not HTTP throughput",
    }


def target_tuning():
    from sklearn.cluster import KMeans
    from threadpoolctl import threadpool_limits

    from common.embeddings import frozen_query
    from common.settings import data_dir

    _, vectors, _, _ = catalog(2000)
    queries = np.stack([frozen_query(f"q{i:03}", data_dir())[0] for i in range(20)])
    with threadpool_limits(limits=1):
        started = time.perf_counter()
        model = KMeans(n_clusters=32, random_state=42, n_init=1).fit(vectors)
        build_seconds = time.perf_counter() - started
        truth = np.argsort(-(queries @ vectors.T), axis=1, kind="stable")[:, :10]

        def evaluate(probes, indexes):
            recalls, timings = [], []
            for _ in range(3):
                for i in indexes:
                    start = time.perf_counter()
                    cells = np.argsort(np.sum((model.cluster_centers_ - queries[i]) ** 2, axis=1))[
                        :probes
                    ]
                    candidates = np.flatnonzero(np.isin(model.labels_, cells))
                    scores = vectors[candidates] @ queries[i]
                    found = candidates[np.argsort(-scores, kind="stable")[:10]]
                    timings.append((time.perf_counter() - start) * 1000)
                    recalls.append(len(set(found) & set(truth[i])) / 10)
            return {
                "recall_at_10": float(np.mean(recalls)),
                "p95_ms": float(np.percentile(timings, 95)),
                "samples": len(timings),
                "latencies_ms": timings,
            }

        development = {p: evaluate(p, range(10)) for p in [1, 4, 8, 16, 32]}
        viable = [
            p for p, r in development.items() if r["recall_at_10"] >= 0.9 and r["p95_ms"] <= 50
        ]
        chosen = min(viable) if viable else None
        heldout = evaluate(chosen, range(10, 20)) if chosen else None
    return {
        "seed": 42,
        "build_seconds": build_seconds,
        "target": {"recall_at_10": 0.9, "p95_ms": 50},
        "development": development,
        "chosen_nprobe": chosen,
        "heldout": heldout,
        "split": "q000–q009 development; q010–q019 test; only 10 distinct queries per split",
        "scope": "Local IVF routing over exact candidates; ANN recall, not semantic relevance",
    }
