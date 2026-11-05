"""Compare the exact kernel with native FAISS.

Concepts: flat index, squared L2, score direction, neighbor agreement.
Run: uv run --extra libs python modules/01_vectors_similarity/examples/02_production.py
Expected: same L2 neighbor order; FAISS returns squared distance
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

# course-extra: libs
import faiss
import numpy as np

from common.teaching import hand_features
from tinyvec.exact import exact_knn


def main() -> None:
    ids, matrix, query = hand_features()
    faiss.omp_set_num_threads(1)
    index = faiss.IndexFlatL2(matrix.shape[1])
    index.add(matrix)
    squared, positions = index.search(query[None, :], len(ids))
    expected = exact_knn(matrix, query, ids, len(ids), "l2")
    actual = [ids[int(i)] for i in positions[0]]
    assert actual == [key for key, _ in expected]
    # KEY IDEA: convert squared distance before comparing to TinyVec's negative L2 score.
    np.testing.assert_allclose(-np.sqrt(squared[0]), [score for _, score in expected], atol=1e-6)
    print("Agreement:", actual)
    print("FAISS squared distances:", squared[0].round(4).tolist())


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
