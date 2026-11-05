"""Learn coarse centroids and visit the closest inverted lists."""

import numpy as np
from threadpoolctl import threadpool_limits


def cluster(matrix, count, seed, iterations=12):
    if count < 1 or not len(matrix):
        raise ValueError("Training requires rows and a positive codebook size")
    rng = np.random.default_rng(seed)
    centers = matrix[rng.choice(len(matrix), min(count, len(matrix)), replace=False)].copy()
    with threadpool_limits(limits=1):
        for _ in range(iterations):
            # Squared Euclidean distance, dropping the row norm common to every center.
            labels = np.argmin((centers * centers).sum(axis=1) - 2 * matrix @ centers.T, axis=1)
            updated = centers.copy()
            for i in range(len(centers)):
                members = matrix[labels == i]
                if len(members):
                    updated[i] = members.mean(axis=0)
            if np.allclose(updated, centers):
                break
            centers = updated
        labels = np.argmin((centers * centers).sum(axis=1) - 2 * matrix @ centers.T, axis=1)
    return centers, labels


class IVF:
    def __init__(self, matrix, nlist=16, nprobe=4, seed=42):
        if not 1 <= nprobe <= nlist:
            raise ValueError("Require 1 <= nprobe <= nlist")
        self.centers, labels = cluster(matrix, nlist, seed)
        self.nprobe = nprobe
        self.lists = [
            np.flatnonzero(labels == i).astype(np.int32) for i in range(len(self.centers))
        ]

    def candidates(self, query, count):
        probes = np.argsort(np.sum((self.centers - query) ** 2, axis=1), kind="stable")[
            : self.nprobe
        ]
        return np.concatenate([self.lists[i] for i in probes])

    @property
    def payload_bytes(self):
        return self.centers.nbytes + sum(rows.nbytes for rows in self.lists)
