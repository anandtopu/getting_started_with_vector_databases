"""Behavioral regressions for candidate selection, mutable snapshots and disk scans."""

import numpy as np
import pytest

from common.index_lessons import prefix_results
from common.stores.ann import IndexedTinyVec
from common.stores.types import CollectionSpec, Record
from tinyvec.hnsw import HNSW
from tinyvec.hybrid import BM25, fuse, maxsim
from tinyvec.mmap import experiment
from tinyvec.pq import PQ


@pytest.mark.parametrize(
    "kind,params",
    [
        ("lsh", {"bits": 2}),
        ("ivf", {"nlist": 4, "nprobe": 4}),
        ("hnsw", {"M": 4}),
        ("pq", {"parts": 2}),
        ("scalar", {}),
        ("binary", {}),
    ],
)
def test_mutate_save_restore(kind, params, tmp_path):
    rng = np.random.default_rng(24)
    rows = [
        Record(str(i), v, {"region": "north" if i % 2 else "east"}, f"boot size {i}")
        for i, v in enumerate(rng.normal(size=(64, 8)))
    ]
    store = IndexedTinyVec(kind, **params)
    store.create_collection(CollectionSpec("test", 8))
    store.insert(rows)
    found = store.search(rows[5].vector, 4, {"op": "eq", "field": "region", "value": "north"})
    assert found and all(h.metadata["region"] == "north" for h in found)
    store.delete([found[0].id])
    store.upsert([Record("new", rows[5].vector, {"region": "north"}, "boots")])
    now = store.search(rows[5].vector, 10)
    assert found[0].id not in [r.id for r in now]
    store.save(tmp_path)
    restored = IndexedTinyVec.load(tmp_path)
    assert restored.snapshot_options() == store.snapshot_options()
    assert [r.id for r in restored.search(rows[5].vector, 10)] == [r.id for r in now]


def test_graph_reachability_with_duplicates():
    matrix = np.repeat(np.eye(4, dtype=np.float32), 12, axis=0)
    graph = HNSW(matrix, M=4, efConstruction=12)
    for layer in graph.layers:
        reached = set()
        todo = [next(iter(layer))]
        while todo:
            node = todo.pop()
            if node not in reached:
                reached.add(node)
                todo.extend(layer[node])
        assert reached == set(layer)
        assert all(len(edges) <= 4 and node not in edges for node, edges in layer.items())
    assert set(graph.filtered_candidates(matrix[0], 3, {35, 36, 47})) == {35, 36, 47}


def test_pq_lookup_agrees_with_explicit_reconstruction():
    matrix = np.random.default_rng(421).normal(size=(80, 8)).astype("float32")
    pq = PQ(matrix, parts=2, centroids=8)
    rebuilt = np.concatenate([b[pq.codes[:, i]] for i, b in enumerate(pq.books)], axis=1)
    actual = pq.candidates(matrix[4], 10)
    np.testing.assert_allclose(
        (rebuilt @ matrix[4])[actual], np.sort(rebuilt @ matrix[4])[::-1][:10], rtol=1e-5
    )
    with pytest.raises(ValueError):
        PQ(matrix, parts=3)


def test_lexical_ids_and_token_interactions():
    scores = BM25(["desk mug SKU-03", "desk mug", "hiking boots"])
    assert scores.rank("SKU-03") == [0] and scores.rank("mug", {1}) == [1]
    assert fuse([["a", "a"], ["b", "a"]])[0][0] == "a"
    assert maxsim([[1, 0], [0, 1]], [[0, 1], [1, 0]]) == 2
    with pytest.raises(ValueError):
        maxsim([[1, 0]], [])
    prefixes = prefix_results()
    assert len(prefixes["32"]["top10"]) == 10
    assert prefixes["1024"]["vector_bytes"] == 32 * prefixes["32"]["vector_bytes"]


def test_disk_handles_partial_last_block(tmp_path):
    result = experiment(tmp_path, rows=103, dimensions=8, block=17)
    assert result["bytes_per_scan"] == 824 and min(result["recall_at_10"]) >= 0.8


def test_hybrid_identifier_beats_unrelated_dense_neighbor():
    store = IndexedTinyVec(kind="ivf", nlist=1, nprobe=1)
    store.create_collection(CollectionSpec("parts", 2))
    store.insert(
        [
            Record("a", [1, 0], {"sku": "A-01"}, "gloves"),
            Record("z", [0, 1], {"sku": "Z-99"}, "boots"),
        ]
    )
    assert store.hybrid_search("z-99", [1, 0], 1)[0].id == "z"
    assert (
        store.hybrid_search("z-99", [1, 0], 1, {"op": "eq", "field": "sku", "value": "A-01"})[0].id
        == "a"
    )


def test_failed_build_does_not_become_empty_search():
    store = IndexedTinyVec(kind="pq", parts=3)
    store.create_collection(CollectionSpec("parts", 2))
    store.upsert([Record("a", [1, 0])])
    for _ in range(2):
        with pytest.raises(ValueError, match="divide"):
            store.search([1, 0])
