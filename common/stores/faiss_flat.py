"""Exact FAISS scoring with TinyVec-owned records, filters and snapshot format.

This is a library adapter, not a server. It deliberately returns all eligible
scores before stable ID sorting so boundary ties follow the shared contract.
Filtered requests build a temporary flat index; that cost is in query latency.
"""

import copy

import numpy as np

from common.errors import CourseError
from common.stores.filters import matches, parse_filter
from common.stores.types import Hit, checked_vector
from tinyvec import TinyVec


class FaissFlatStore(TinyVec):
    def __init__(self) -> None:
        super().__init__()
        try:
            import faiss
        except ImportError as exc:
            raise CourseError("Install the exact library comparison: uv sync --extra libs") from exc
        self.faiss = faiss
        self.faiss.omp_set_num_threads(1)
        self._index = None

    def _flat(self, matrix: np.ndarray):
        spec = self._require_spec()
        values = np.ascontiguousarray(matrix, dtype=np.float32).copy()
        if spec.metric == "cosine":
            self.faiss.normalize_L2(values)
        index = (
            self.faiss.IndexFlatL2(spec.dimensions)
            if spec.metric == "l2"
            else self.faiss.IndexFlatIP(spec.dimensions)
        )
        index.add(values)
        return index

    def build(self) -> None:
        super().build()
        self._index = self._flat(self._matrix)

    def search(self, vector, k: int = 10, filter=None, *, space=None) -> list[Hit]:
        spec = self._require_spec()
        if isinstance(k, bool) or not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        if space is not None and space != spec.space:
            raise ValueError("Query embedding space does not match this collection")
        query = checked_vector(vector, spec).reshape(1, -1)
        expression = parse_filter(filter)
        if self._matrix is None:
            self.build()
        positions = [
            i for i, key in enumerate(self._ids) if matches(self._records[key].metadata, expression)
        ]
        if not positions:
            return []
        index = self._index if expression is None else self._flat(self._matrix[positions])
        if spec.metric == "cosine":
            self.faiss.normalize_L2(query)
        distances, offsets = index.search(query, len(positions))
        winners = []
        for native, offset in zip(distances[0], offsets[0], strict=True):
            key = self._ids[positions[int(offset)]]
            score = -float(np.sqrt(max(0.0, native))) if spec.metric == "l2" else float(native)
            winners.append((score, key, float(native)))
        winners.sort(key=lambda item: (-item[0], item[1]))
        return [
            Hit(
                key,
                score,
                copy.deepcopy(self._records[key].metadata),
                self._records[key].text,
                native,
            )
            for score, key, native in winners[:k]
        ]

    def close(self) -> None:
        self._index = None
        super().close()
