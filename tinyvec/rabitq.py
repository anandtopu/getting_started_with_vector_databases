"""Readable one-bit RaBitQ estimator; dense evaluation, no SIMD or pruning claims.

Center x, rotate its unit direction, store sign bits and its inner product with
that signed unit vector. Divide the query/code inner product by that correction
before reconstructing squared L2 distance. See Gao and Long, SIGMOD 2024.
"""

import numpy as np


class RaBitQ:
    def __init__(self, matrix, seed=42):
        matrix = np.asarray(matrix, dtype=np.float32)
        if (
            matrix.ndim != 2
            or not len(matrix)
            or matrix.shape[1] == 0
            or not np.isfinite(matrix).all()
        ):
            raise ValueError("Expected a nonempty finite matrix")
        self.dimensions = matrix.shape[1]
        self.center = matrix.mean(axis=0)
        centered = matrix - self.center
        self.norms = np.linalg.norm(centered, axis=1)
        rng = np.random.default_rng(seed)
        rotation, triangular = np.linalg.qr(rng.normal(size=(self.dimensions, self.dimensions)))
        self.rotation = (rotation * np.where(np.diag(triangular) >= 0, 1.0, -1.0)).astype(
            np.float32
        )
        directions = centered / np.maximum(self.norms[:, None], 1e-20)
        rotated = directions @ self.rotation
        signs = np.where(rotated >= 0, 1.0, -1.0).astype(np.float32) / np.sqrt(self.dimensions)
        self.correction = np.sum(signs * rotated, axis=1)
        self.bits = np.packbits(rotated >= 0, axis=1)

    def distances(self, query):
        query = np.asarray(query, dtype=np.float32)
        if query.shape != (self.dimensions,) or not np.isfinite(query).all():
            raise ValueError("Invalid query dimensions or values")
        centered = query - self.center
        signs = (
            np.unpackbits(self.bits, axis=1, count=self.dimensions).astype(np.float32) * 2 - 1
        ) / np.sqrt(self.dimensions)
        # KEY IDEA: the correction estimates the original dot product, not Hamming distance.
        inner = (signs @ (centered @ self.rotation)) / np.maximum(self.correction, 1e-20)
        return self.norms**2 + centered @ centered - 2 * self.norms * inner

    def candidates(self, query, count):
        if count < 1:
            raise ValueError("Candidate count must be positive")
        return np.argsort(self.distances(query), kind="stable")[:count]

    @property
    def payload_bytes(self):
        return (
            self.bits.nbytes
            + self.norms.nbytes
            + self.correction.nbytes
            + self.center.nbytes
            + self.rotation.nbytes
        )
