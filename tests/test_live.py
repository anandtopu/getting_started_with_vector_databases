import numpy as np
import pytest

from common.embeddings import TextEncoder


@pytest.mark.live
def test_cached_minilm_has_semantic_signal():
    vectors = TextEncoder().encode(
        [
            "keep coffee hot on my desk",
            "a heated coaster for a coffee mug",
            "waterproof hiking boots",
        ]
    )
    assert vectors.shape == (3, 384)
    assert np.dot(vectors[0], vectors[1]) > np.dot(vectors[0], vectors[2])
