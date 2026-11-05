"""Asymmetric inner-product lookup over learned subvector codebooks."""

import numpy as np

from tinyvec.ivf import cluster


class PQ:
    def __init__(self, matrix, parts=8, centroids=16, seed=42):
        if parts < 1 or matrix.shape[1] % parts or not 1 <= centroids <= 256:
            raise ValueError("parts must divide the dimension; use 1–256 centroids")
        self.books = []
        codes = []
        for i, block in enumerate(np.split(matrix, parts, axis=1)):
            centers, labels = cluster(block, centroids, seed + i)
            self.books.append(centers)
            codes.append(labels.astype(np.uint8))
        self.codes = np.stack(codes, axis=1)

    def candidates(self, query, count):
        scores = np.zeros(len(self.codes), dtype=np.float32)
        for i, (book, part) in enumerate(
            zip(self.books, np.split(query, len(self.books)), strict=True)
        ):
            scores += (book @ part)[self.codes[:, i]]
        return np.argsort(-scores, kind="stable")[:count]

    @property
    def payload_bytes(self):
        return self.codes.nbytes + sum(b.nbytes for b in self.books)
