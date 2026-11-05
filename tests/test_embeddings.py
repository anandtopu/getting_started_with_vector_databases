from dataclasses import replace

import numpy as np

from common.embeddings import EmbeddingCache, HashEncoder


def test_hash_and_cache_are_stable_and_role_revision_sensitive(tmp_path):
    encoder = HashEncoder(32)
    texts = ["cozy chair", "warm coffee", "cozy chair"]
    calls = []

    def encode(texts, role):
        calls.append((texts, role))
        return encoder.encode(texts, role)

    cache = EmbeddingCache(tmp_path)
    first = cache.encode(texts, encoder.spec, "document", encode)
    second = cache.encode(texts, encoder.spec, "document", encode)
    assert len(calls) == 1
    assert len(calls[0][0]) == 2
    np.testing.assert_array_equal(first, second)
    np.testing.assert_allclose(np.linalg.norm(first, axis=1), 1)
    cache.encode(texts, encoder.spec, "query", encode)
    cache.encode(texts, replace(encoder.spec, revision="v2"), "query", encode)
    assert len(calls) == 3
    assert cache.encode([], encoder.spec, "query", encode).shape == (0, 32)
