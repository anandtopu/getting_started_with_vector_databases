"""Find duplicate candidates without comparing every product pair.

Concepts: Find duplicate candidates without comparing every product pair.
Run: uv run python modules/05_ann_lsh/use_case/duplicate_candidates.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import unit_catalog
from tinyvec.lsh import LSH


def main():
    products, matrix, _ = unit_catalog(400)
    index = LSH(matrix, bits=7, tables=6)
    source = 0
    shortlist = [i for i in index.candidates(matrix[source], 5) if i != source]
    ranked = sorted(shortlist, key=lambda i: -float(matrix[i] @ matrix[source]))
    print(
        "anchor",
        products.iloc[source].title,
        "review",
        products.iloc[ranked[:3]].title.tolist(),
        "candidate count",
        len(shortlist),
    )
    assert source not in ranked


if __name__ == "__main__":
    main()
