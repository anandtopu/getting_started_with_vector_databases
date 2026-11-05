import numpy as np
import pytest

from tinyvec.exact import exact_knn


def test_hand_geometry_and_ties():
    assert exact_knn(np.array([[1, 0], [0, 1], [1, 0]]), np.array([1, 0]), ["b", "c", "a"], 2) == [
        ("a", 1.0),
        ("b", 1.0),
    ]
    assert exact_knn(np.empty((0, 2)), np.array([1, 0]), [], 2) == []
    with pytest.raises(ValueError):
        exact_knn(np.array([[0, 0]]), np.array([1, 0]), ["zero"])


@pytest.mark.parametrize("metric", ["cosine", "dot", "l2"])
def test_faiss_against_independent_reference(metric):
    pytest.importorskip("faiss")
    from common.bench.ground_truth import exact_neighbors
    from common.stores.faiss_flat import FaissFlatStore
    from common.stores.types import CollectionSpec, Record

    rng = np.random.default_rng(20261104)
    vectors = rng.normal(size=(20, 8)).astype(np.float32)
    query = rng.normal(size=8).astype(np.float32)
    ids = [f"p{i:02}" for i in range(20)]
    store = FaissFlatStore()
    store.create_collection(CollectionSpec("math", 8, metric, "math-v1"))
    store.upsert([Record(key, v) for key, v in zip(ids, vectors, strict=True)])
    try:
        assert [h.id for h in store.search(query, 7)] == exact_neighbors(
            vectors, ids, [{}] * 20, query, 7, metric
        )
    finally:
        store.close()
