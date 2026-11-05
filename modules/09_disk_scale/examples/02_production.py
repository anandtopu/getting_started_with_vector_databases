"""Reopen a USearch graph through its memory-mapped view.

Concepts: Reopen a USearch graph through its memory-mapped view.
Run: uv run --extra libs python modules/09_disk_scale/examples/02_production.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

# course-extra: libs
import tempfile
from pathlib import Path

import numpy as np
from usearch.index import Index

from common.index_lessons import unit_catalog


def main():
    _, matrix, q = unit_catalog(320)
    with tempfile.TemporaryDirectory() as directory:
        path = str(Path(directory) / "products.usearch")
        index = Index(ndim=matrix.shape[1], metric="cos", dtype="f32")
        index.add(np.arange(len(matrix), dtype=np.uint64), matrix, threads=1)
        index.save(path)
        view = Index.restore(path, view=True)
        before = index.search(q, 5, threads=1).keys.tolist()
        after = view.search(q, 5, threads=1).keys.tolist()
        assert before == after
        print("restored IDs", after, "file bytes", Path(path).stat().st_size)
        del view, index


if __name__ == "__main__":
    main()
