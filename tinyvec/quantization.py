"""Symmetric int8 calibration and packed sign codes for angular search."""

import numpy as np


class Scalar:
    def __init__(self, matrix):
        peak = np.max(np.abs(matrix), axis=0)
        self.step = np.where(peak > 0, peak / 127, 1).astype(np.float32)
        self.codes = np.rint(matrix / self.step).clip(-127, 127).astype(np.int8)

    def candidates(self, query, count):
        scores = self.codes @ (query * self.step)
        return np.argsort(-scores, kind="stable")[:count]

    @property
    def payload_bytes(self):
        return self.codes.nbytes + self.step.nbytes


class Binary:
    def __init__(self, matrix):
        self.codes = np.packbits(matrix >= 0, axis=1)

    def candidates(self, query, count):
        different = np.bitwise_xor(self.codes, np.packbits(query >= 0))
        hamming = np.bitwise_count(different).sum(axis=1)
        return np.argsort(hamming, kind="stable")[:count]

    @property
    def payload_bytes(self):
        return self.codes.nbytes
