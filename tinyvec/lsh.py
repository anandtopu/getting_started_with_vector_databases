"""Random hyperplane hash tables for angular nearest neighbors."""

from collections import defaultdict

import numpy as np


class LSH:
    def __init__(self, matrix, bits=6, tables=8, seed=42):
        if not (1 <= bits <= 32 and tables >= 1):
            raise ValueError("Use 1–32 bits and at least one table")
        rng = np.random.default_rng(seed)
        self.planes = rng.standard_normal((tables, bits, matrix.shape[1]), dtype=np.float32)
        self.tables = []
        for planes in self.planes:
            buckets = defaultdict(list)
            for row, key in enumerate(np.packbits(matrix @ planes.T >= 0, axis=1)):
                buckets[key.tobytes()].append(row)
            self.tables.append(buckets)

    def candidates(self, query, count):
        found = set()
        for planes, buckets in zip(self.planes, self.tables, strict=True):
            key = np.packbits(planes @ query >= 0).tobytes()
            found.update(buckets.get(key, ()))
        return sorted(found)

    @property
    def payload_bytes(self):
        return self.planes.nbytes + sum(
            len(key) + 4 * len(rows) for table in self.tables for key, rows in table.items()
        )
