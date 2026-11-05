"""Run the same lifecycle against installed engines and explicitly enabled local servers."""

import os

import pytest

from common.settings import cache_dir
from common.stores.registry import make_store
from common.stores.types import CollectionSpec, Record

EMBEDDED = {"chroma": "chromadb", "lancedb": "lancedb", "duckdb": "duckdb"}
SERVERS = ["pgvector", "qdrant", "weaviate", "milvus", "elasticsearch", "redis", "mongodb", "vespa"]


def test_partial_native_write_cannot_publish_a_trusted_snapshot(tmp_path):
    from common.errors import CourseError
    from common.stores.database import DatabaseStore

    class PartialStore(DatabaseStore):
        def _create(self, spec):
            self.native = {}

        def _put(self, rows):
            first = next(iter(rows))
            self.native[first] = rows[first]
            raise ConnectionError("write acknowledgement lost")

        def _drop(self):
            self.native.clear()

        def _disconnect(self):
            self.disconnected = True

    store = PartialStore()
    store.create_collection(CollectionSpec("partial", 2))
    with pytest.raises(ConnectionError):
        store.upsert([Record("a", [1, 0]), Record("b", [0, 1])])
    for action in (
        lambda: store.search([1, 0]),
        lambda: store.save(tmp_path),
        lambda: store.upsert([]),
    ):
        with pytest.raises(CourseError, match="partially applied"):
            action()
    store.close()
    assert not store.native and store.disconnected


def verify(backend, tmp_path):
    path = cache_dir() / "tier3/chroma" if backend == "chroma" else tmp_path / "database"

    def open_store(path):
        return make_store(backend, path=path)

    spec = CollectionSpec("lesson", 3, "cosine", "lesson-3")
    rows = [
        Record("a", [1, 0, 0], {"price": 10, "region": "north", "active": True}, "mug warmer"),
        Record("b", [0, 1, 0], {"price": 11, "region": "south"}, "chair"),
        Record("c", [0, 0, 1], {"price": 9, "region": "north"}, "lamp"),
    ]
    store = open_store(path)
    try:
        store.create_collection(spec)
        assert store.search([1, 0, 0]) == []
        store.upsert(rows)
        old = store.search([1, 0, 0], 2)
        assert old[0].id == "a"
        with pytest.raises(ValueError):
            store.upsert([rows[1], Record("bad", [1, 0])])
        with pytest.raises(ValueError):
            store.search([1, 0, 0], space="wrong")
        with pytest.raises(ValueError):
            store.search([0, 0, 0])
        assert store.search([1, 0, 0], filter={"op": "eq", "field": "active", "value": 1}) == []
        eligible = store.search(
            [1, 0, 0],
            filter={
                "op": "and",
                "clauses": [
                    {"op": "eq", "field": "region", "value": "north"},
                    {"op": "lt", "field": "price", "value": 10},
                ],
            },
        )
        assert [r.id for r in eligible] == ["c"]
        store.upsert([Record("a", [0, -1, 0], {"region": "north", "price": 20}, "updated")])
        assert store.search([0, -1, 0], 1)[0].text == "updated"
        store.delete(["b", "missing"])
        assert {r.id for r in store.search([1, 0, 0], 5)} == {"a", "c"}
        if store.capabilities.hybrid != "none":
            hits = store.hybrid_search(
                "updated", [0, -1, 0], 2, {"op": "eq", "field": "region", "value": "north"}
            )
            assert hits and all(h.metadata["region"] == "north" for h in hits)
        store.save(tmp_path / "snapshot")
        restored = open_store(path if backend == "chroma" else tmp_path / "restored")
        try:
            restored.restore(tmp_path / "snapshot")
            assert restored.search([0, -1, 0], 1)[0].id == "a"
            assert [r.id for r in restored.search([0, 0, 1], 5)] == ["c", "a"]
        finally:
            restored.close()
    finally:
        store.close()


@pytest.mark.allow_hosts(["127.0.0.1", "::1"])
@pytest.mark.parametrize("backend", EMBEDDED)
def test_embedded_database_lifecycle(backend, tmp_path):
    pytest.importorskip(EMBEDDED[backend])
    verify(backend, tmp_path)


@pytest.mark.docker
@pytest.mark.allow_hosts(["127.0.0.1", "::1", "localhost"])
@pytest.mark.parametrize("backend", SERVERS)
def test_server_database_lifecycle(backend, tmp_path):
    enabled = os.environ.get("MARLOWE_TEST_DATABASE", "").split(",")
    if backend not in enabled:
        pytest.skip(f"Start {backend} and set MARLOWE_TEST_DATABASE")
    verify(backend, tmp_path)
