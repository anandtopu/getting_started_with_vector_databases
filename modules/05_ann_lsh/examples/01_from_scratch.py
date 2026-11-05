"""Hash a product into buckets using random hyperplane signs.

Concepts: Hash a product into buckets using random hyperplane signs.
Run: uv run python modules/05_ann_lsh/examples/01_from_scratch.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

import numpy as np

from common.index_lessons import unit_catalog
from tinyvec.lsh import LSH


def main():
    products, matrix, query = unit_catalog(240)
    index = LSH(matrix, bits=6, tables=4, seed=17)
    # KEY IDEA: only rows sharing a complete signature in at least one table survive.
    candidates = index.candidates(query, 10)
    exact = np.argsort(-(matrix @ query))[:10]
    print(
        "rows inspected",
        len(candidates),
        "of",
        len(matrix),
        "true neighbors retained",
        len(set(exact) & set(candidates)),
    )
    print(products.iloc[candidates].title.head().tolist())
    assert len(candidates) == len(set(candidates))


if __name__ == "__main__":
    main()
