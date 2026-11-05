"""Durability, corruption, concurrency and randomized-quantizer invariants."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from common.stores.types import CollectionSpec, Record
from tinyvec.durable import DurableTinyVec
from tinyvec.rabitq import RaBitQ


def test_wal_crash_tail_checkpoint_and_delete(tmp_path):
    spec = CollectionSpec("wal", 2)
    with DurableTinyVec(tmp_path, spec) as db:
        db.upsert([Record("a", np.array([1.0, 0]), {"tenant": "a"})])
        db.checkpoint()
        db.upsert([Record("b", np.array([0.0, 1]), {"tenant": "b"})])
        db.delete(["a"])
    with (tmp_path / "mutations.jsonl").open("ab") as stream:
        stream.write(b'{"payload":')
    with DurableTinyVec(tmp_path, spec) as restored:
        assert [h.id for h in restored.search([1, 0])] == ["b"]
        assert restored.wal.sequence == 3
        with pytest.raises(ValueError):
            DurableTinyVec(tmp_path, spec)
        with pytest.raises(ValueError):
            restored.upsert([Record("bad", np.array([1.0, 2.0, 3.0]))])
        assert restored.wal.sequence == 3


def test_full_frame_corruption_fails_closed(tmp_path):
    spec = CollectionSpec("wal", 2)
    with DurableTinyVec(tmp_path, spec) as db:
        db.upsert([Record("a", np.array([1.0, 0]))])
    path = tmp_path / "mutations.jsonl"
    entry = json.loads(path.read_text())
    entry["payload"]["data"][0]["id"] = "tampered"
    path.write_text(json.dumps(entry) + "\n")
    with pytest.raises(ValueError, match="checksum"):
        DurableTinyVec(tmp_path, spec)


def test_concurrent_reads_and_writes(tmp_path):
    with DurableTinyVec(tmp_path, CollectionSpec("wal", 2)) as db:

        def task(i):
            db.upsert([Record(str(i), np.array([1.0, i / 100]))])
            assert db.search([1, 0], k=1)

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(task, range(20)))
        assert len(db.store.records()) == 20 and db.wal.sequence == 20


def test_acknowledged_write_survives_process_exit(tmp_path):
    code = "import os,sys,numpy as np; from pathlib import Path; from tinyvec.durable import DurableTinyVec; from common.stores.types import CollectionSpec,Record; d=DurableTinyVec(Path(sys.argv[1]),CollectionSpec('crash',2)); d.upsert([Record('durable',np.array([1.,0.]))]); os._exit(19)"
    proc = subprocess.run([sys.executable, "-c", code, str(tmp_path)], check=False)
    assert proc.returncode == 19
    with DurableTinyVec(tmp_path, CollectionSpec("crash", 2)) as db:
        assert db.search([1, 0])[0].id == "durable"


def test_rabitq_self_distance_rotation_and_shape():
    with pytest.raises(ValueError):
        RaBitQ(np.empty((2, 0)))
    identical = RaBitQ(np.ones((3, 2)))
    np.testing.assert_allclose(identical.distances([1, 1]), 0)
    matrix = np.random.default_rng(1).normal(size=(30, 16)).astype(np.float32)
    index = RaBitQ(matrix)
    np.testing.assert_allclose(index.rotation.T @ index.rotation, np.eye(16), atol=1e-6)
    for i in [0, 5, 20]:
        assert abs(index.distances(matrix[i])[i]) < 1e-4
    assert np.isfinite(RaBitQ(np.ones((4, 8))).distances(np.ones(8))).all()
    with pytest.raises(ValueError):
        index.distances([1, 2])


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_durable_http_lifecycle(tmp_path):
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from tinyvec.service import create_app

    with TestClient(create_app(tmp_path)) as client:
        assert (
            client.post("/records", json={"records": [{"id": "a", "vector": [1, 0]}]}).json()[
                "sequence"
            ]
            == 1
        )
        assert client.post("/search", json={"vector": [1, 0]}).json()[0]["id"] == "a"
        assert client.post("/search", json={"vector": [1, 0], "space": "wrong"}).status_code == 400
        assert client.post("/checkpoint").status_code == 200
    with TestClient(create_app(tmp_path)) as client:
        assert client.get("/health").json()["sequence"] == 1
        assert client.delete("/records/a").json()["sequence"] == 2
        assert client.post("/search", json={"vector": [1, 0]}).json() == []
