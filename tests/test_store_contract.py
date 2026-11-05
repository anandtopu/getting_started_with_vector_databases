"""The same behavioral contract runs against TinyVec and real embedded SQLite-vec."""

import numpy as np
import pytest

from common.errors import CourseError
from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


def test_exact_order_ties_and_metadata_copies(store, rows):
    store.upsert(rows)
    hits = store.search([1, 0, 0], 10, space="fixture-v1")
    assert [h.id for h in hits] == ["a", "d", "b", "c"]
    hits[0].metadata["tenant"] = "changed"
    assert store.search([1, 0, 0], 1)[0].metadata["tenant"] == "one"


def test_upsert_delete_and_atomic_validation(store, rows):
    store.upsert(rows)
    with pytest.raises(ValueError):
        store.upsert([Record("a", np.array([0, 1, 0]), {}), Record("bad", np.array([1, 2]), {})])
    assert store.search([1, 0, 0], 1)[0].id == "a"
    store.upsert([Record("a", np.array([0, 0, 1]), {"tenant": "one"}, "updated")])
    assert store.search([0, 0, 1], 1)[0].text == "updated"
    store.delete(["a", "missing"])
    assert "a" not in [h.id for h in store.search([0, 0, 1], 10)]


@pytest.mark.parametrize(
    "expression,expected",
    [
        ({"op": "eq", "field": "tenant", "value": "one"}, {"a", "c", "d"}),
        ({"op": "eq", "field": "missing", "value": None}, set()),
        ({"op": "eq", "field": "active", "value": 1}, set()),
        ({"op": "eq", "field": "active", "value": True}, {"a"}),
        ({"op": "eq", "field": "price", "value": 9}, set()),
        ({"op": "in", "field": "tenant", "value": []}, set()),
        ({"op": "in", "field": "tenant", "value": ["one", "two"]}, {"a", "b", "c", "d"}),
        ({"op": "lt", "field": "price", "value": 11}, {"a", "c"}),
        (
            {
                "op": "and",
                "clauses": [
                    {"op": "eq", "field": "tenant", "value": "one"},
                    {"op": "gt", "field": "stock", "value": 2},
                ],
            },
            {"c"},
        ),
        (
            {
                "op": "or",
                "clauses": [
                    {"op": "eq", "field": "tenant", "value": "two"},
                    {"op": "lt", "field": "price", "value": 10},
                ],
            },
            {"b", "c"},
        ),
    ],
)
def test_filters_apply_to_eligible_neighbors(store, rows, expression, expected):
    store.upsert(rows)
    assert {h.id for h in store.search([1, 0, 0], 10, expression)} == expected


def test_tenant_constraint_and_injection(store, rows):
    store.upsert(rows)
    assert all(
        h.metadata["tenant"] == "two"
        for h in store.search([1, 0, 0], 10, {"op": "eq", "field": "tenant", "value": "two"})
    )
    assert (
        store.search([1, 0, 0], 10, {"op": "eq", "field": "tenant", "value": "' OR 1=1 --"}) == []
    )


@pytest.mark.parametrize("query", [[0, 0, 0], [1, 2], [float("nan"), 0, 1]])
def test_invalid_vectors_are_rejected(store, query):
    with pytest.raises(ValueError):
        store.search(query)


def test_empty_space_and_capabilities(store):
    assert store.search([1, 0, 0]) == []
    with pytest.raises(ValueError, match="space"):
        store.search([1, 0, 0], space="different-model")
    with pytest.raises(ValueError):
        store.search([1, 0, 0], k=0)
    with pytest.raises(CourseError):
        store.hybrid_search("coffee", [1, 0, 0])
    with pytest.raises(ValueError):
        store.create_collection(CollectionSpec("wrong", 7))


@pytest.mark.parametrize("value", [{"nested": 1}, float("nan"), float("inf")])
def test_invalid_filter_values_rejected_consistently(store, value):
    with pytest.raises(ValueError):
        store.search([1, 0, 0], filter={"op": "eq", "field": "price", "value": value})


def test_persistence(store, rows, tmp_path):
    store.upsert(rows)
    store.save(tmp_path / "snapshot")
    if isinstance(store, TinyVec):
        restored = type(store).load(tmp_path / "snapshot")
    else:
        from common.stores.sqlite_vec import SQLiteVecStore

        restored = SQLiteVecStore(tmp_path / "snapshot/snapshot.db")
    try:
        assert restored.spec == store.spec
        assert [h.id for h in restored.search([1, 0, 0], 10)] == [
            h.id for h in store.search([1, 0, 0], 10)
        ]
    finally:
        restored.close()
