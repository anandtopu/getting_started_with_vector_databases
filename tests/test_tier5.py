"""Negative tenant, mutation, restore, admission and cache checks."""

import json

import numpy as np
import pytest

from common.ops.backup import Backups
from common.ops.cache import QueryCache
from common.ops.ingestion import ingest, stable_id
from common.ops.migration import ModelRouter
from common.ops.replication import ReplicaSimulation
from common.security.deletion import DeletionLedger
from common.security.identity import Keyring, Principal
from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


def test_cache_scope_expiry_and_copy():
    clock = [0.0]
    cache = QueryCache(capacity=1, ttl=2, clock=lambda: clock[0])
    first = cache.key("a", "model1", 0, "search", {"filter": None})
    assert first != cache.key("b", "model1", 0, "search", {"filter": None})
    assert first != cache.key("a", "model1", 1, "search", {"filter": None})
    cache.put(first, {"ids": ["private"]})
    result = cache.get(first)
    result["ids"].clear()
    assert cache.get(first)["ids"] == ["private"]
    clock[0] = 2
    assert cache.get(first) is None


def test_ingestion_bounded_replay():
    storage = {}

    def write(batch):
        storage.update(batch)

    rows = [(stable_id("a", str(i)), i) for i in range(15)]
    first = ingest(rows, write, batch_size=3, pending_limit=2)
    ingest(rows, write, batch_size=3)
    assert len(storage) == 15 and first["max_pending_batches"] <= 2
    assert stable_id("a", "1") != stable_id("b", "1")
    assert stable_id("a\0b", "c") != stable_id("a", "b\0c")
    with pytest.raises(RuntimeError):
        ingest([1], lambda _: (_ for _ in ()).throw(RuntimeError("partial write")))


def test_backup_integrity_deletion_and_purge(tmp_path):
    store = TinyVec()
    store.create_collection(CollectionSpec("test", 2))
    store.upsert(
        [
            Record("a", np.array([1.0, 0]), {"seller_id": "one"}),
            Record("b", np.array([0.0, 1]), {"seller_id": "two"}),
        ]
    )
    backups = Backups(tmp_path / "backups")
    name = backups.create(store, watermark=2)
    ledger = DeletionLedger(tmp_path / "deletions.json")
    ledger.deny("one", ["a"])
    restored, metadata = backups.restore(name, DeletionLedger(ledger.path))
    assert [r.id for r in restored.records()] == ["b"] and metadata["watermark"] == 2
    assert backups.purge_containing("one", {"a"}) == [name]
    assert not backups.checked(name).exists()
    with pytest.raises(ValueError):
        backups.checked("../outside")
    name = backups.create(store)
    (backups.checked(name) / "snapshot.json").write_text("{}")
    with pytest.raises(ValueError):
        backups.restore(name, ledger)


def test_model_gate_and_rollback(tmp_path):
    router = ModelRouter(tmp_path / "active.json")
    router.publish("blue", "old", ready=True, measured_recall=1, minimum_recall=0.9)
    with pytest.raises(ValueError):
        router.publish("green", "new", ready=True, measured_recall=0.8, minimum_recall=0.9)
    assert ModelRouter(router.path).route("old") == "blue"
    router.publish("green", "new", ready=True, measured_recall=1, minimum_recall=0.9)
    with pytest.raises(ValueError):
        router.route("old")
    router.rollback()
    assert router.route("old") == "blue"


def test_replica_lag_and_quorum():
    simulation = ReplicaSimulation()
    simulation.write("x", "new", acknowledgements=1)
    assert simulation.read(1, "x") is None
    simulation.tick()
    assert simulation.read(1, "x")[1] == "new"
    simulation.alive = {0}
    with pytest.raises(RuntimeError):
        simulation.write("x", "later", acknowledgements=2)


def test_compaction_preserves_live_rows():
    from tinyvec.storage import VersionedRows

    store = VersionedRows()
    store.upsert("a", 1)
    store.upsert("a", 2)
    store.upsert("b", 3)
    store.delete("b")
    before = store.live()
    assert store.compact()["reclaimed_versions"] == 2
    assert store.live() == before == [("a", 2)]


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_secure_ui_requires_token():
    testing = pytest.importorskip("streamlit.testing.v1")
    from common.settings import ROOT

    app = testing.AppTest.from_file(str(ROOT / "playground/secure_market.py")).run(timeout=30)
    assert not app.exception
    assert app.button[0].disabled
    for mode in ["Help center", "Similar items", "Listing review", "Photos"]:
        app.radio[0].set_value(mode).run()
        assert not app.exception and app.button[0].disabled


@pytest.mark.parametrize("backend", ["tinyvec", "sqlite-vec", "qdrant-local"])
@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
def test_secure_all_routes_and_restart(tmp_path, backend):
    pytest.importorskip("fastapi")
    pytest.importorskip("prometheus_client")
    if backend == "sqlite-vec":
        pytest.importorskip("sqlite_vec")
    if backend == "qdrant-local":
        pytest.importorskip("qdrant_client")
    from fastapi.testclient import TestClient

    from common.apps.secure_api import create_app

    tokens = {
        "reader-one-0123456789": Principal("reader", "seller-000", "reader"),
        "admin-one-0123456789": Principal("admin", "seller-000", "admin"),
        "reader-two-0123456789": Principal("other", "seller-001", "reader"),
    }
    ring = Keyring(tokens)
    a = {"Authorization": "Bearer reader-one-0123456789"}
    admin = {"Authorization": "Bearer admin-one-0123456789"}
    b = {"Authorization": "Bearer reader-two-0123456789"}

    def application():
        return create_app(keyring=ring, root=tmp_path, backend=backend, limit=500)

    with TestClient(application()) as client:
        assert client.post("/search", json={}).status_code == 401
        assert (
            client.post("/search", json={}, headers={"Authorization": "Bearer wrong"}).status_code
            == 401
        )
        assert client.post("/search", json={"tenant": "seller-001"}, headers=a).status_code == 422
        for headers, tenant in [(a, "seller-000"), (b, "seller-001")]:
            response = client.post("/search", json={}, headers=headers)
            assert response.status_code == 200, response.text
            hits = response.json()["data"]["hits"]
            assert hits and all(h["metadata"]["seller_id"] == tenant for h in hits)
            assert client.post("/search", json={}, headers=headers).json()["cached"]
        attack = {
            "op": "or",
            "clauses": [
                {"op": "eq", "field": "seller_id", "value": "seller-001"},
                {"op": "gte", "field": "price", "value": 0},
            ],
        }
        result = client.post(
            "/search", json={"filter": attack, "multilingual": True, "query_id": "q004"}, headers=a
        )
        assert result.status_code == 200 and all(
            h["metadata"]["seller_id"] == "seller-000" for h in result.json()["data"]["hits"]
        )
        assert client.get("/similar/p0000001", headers=a).status_code == 400
        assert (
            client.post(
                "/duplicates",
                json={"first": "p0000000", "second": "p0000001", "threshold": 0.9},
                headers=a,
            ).status_code
            == 400
        )
        assert client.post("/photos", json={"product_id": "p0000001"}, headers=a).status_code == 400
        assert client.post("/help", json={}, headers=a).status_code == 200  # public course policies
        assert client.get("/metrics", headers=a).status_code == 403
        assert client.delete("/listings/p0000000", headers=a).status_code == 403
        assert client.delete("/listings/p0000001", headers=admin).status_code == 404
        assert client.post("/ops/backup", headers=admin).status_code == 200
        response = client.delete("/listings/p0000000", headers=admin)
        assert response.status_code == 200 and response.json()["purged_snapshots"]
        assert client.post("/photos", json={}, headers=admin).status_code == 400
        assert client.get("/metrics", headers=admin).status_code == 200
    with TestClient(application()) as client:
        hits = client.post("/search", json={}, headers=admin).json()["data"]["hits"]
        assert "p0000000" not in [h["id"] for h in hits]
    audit = (tmp_path / "audit.jsonl").read_text()
    assert all(token not in audit for token in tokens) and "q004" not in audit
    assert all(
        set(json.loads(line)) == {"time", "subject", "tenant", "action", "outcome", "request_id"}
        for line in audit.splitlines()
    )
