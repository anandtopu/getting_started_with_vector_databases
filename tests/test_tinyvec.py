import json

import numpy as np
import pytest

from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


@pytest.mark.parametrize("metric", ["cosine", "dot", "l2"])
@pytest.mark.parametrize("block_size", [1, 2, 100])
def test_exact_matches_independent_numpy(metric, block_size):
    matrix = np.array([[1, 2, 3], [3, 2, 1], [1, 1, 1], [-1, 2, 1]], dtype=np.float32)
    query = np.array([2, 1, 0.5], dtype=np.float32)
    reference = matrix @ query
    if metric == "cosine":
        reference /= np.linalg.norm(matrix, axis=1) * np.linalg.norm(query)
    elif metric == "l2":
        reference = -np.linalg.norm(matrix - query, axis=1)
    store = TinyVec(block_size)
    store.create_collection(CollectionSpec("test", 3, metric))
    store.upsert(Record(str(i), row) for i, row in enumerate(matrix))
    hits = store.search(query, 4)
    expected = np.argsort(-reference, kind="stable")
    assert [h.id for h in hits] == list(map(str, expected))
    np.testing.assert_allclose([h.score for h in hits], reference[expected], rtol=1e-6)


def test_snapshot_corruption_and_path_escape(tmp_path):
    store = TinyVec()
    store.create_collection(CollectionSpec("test", 3))
    store.upsert([Record("a", np.ones(3))])
    store.save(tmp_path)
    manifest_path = tmp_path / "snapshot.json"
    manifest = json.loads(manifest_path.read_text())
    (tmp_path / manifest["vectors"]).write_bytes(b"broken")
    with pytest.raises(ValueError, match="checksum"):
        TinyVec.load(tmp_path)
    manifest["vectors"] = "../outside.npy"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="path"):
        TinyVec.load(tmp_path)


def test_insert_conflicts_leave_batch_unapplied():
    store = TinyVec()
    store.create_collection(CollectionSpec("catalog", 2))
    item = Record("mug", np.array([1, 0]))
    other = Record("flask", np.array([0, 1]))
    store.insert([item])
    with pytest.raises(ValueError, match="unique IDs"):
        store.insert([other, item])
    with pytest.raises(ValueError, match="unique IDs"):
        store.insert([other, other])
    assert [record.id for record in store.records()] == ["mug"]
