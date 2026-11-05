"""A mutable TinyVec collection with a rebuildable, seeded angular candidate index."""

import copy

import numpy as np

from common.stores.filters import parse_filter
from common.stores.types import Capabilities, Hit, checked_vector
from tinyvec import TinyVec
from tinyvec.filters import MetadataIndex
from tinyvec.hnsw import HNSW
from tinyvec.hybrid import BM25, fuse
from tinyvec.ivf import IVF
from tinyvec.lsh import LSH
from tinyvec.pq import PQ
from tinyvec.quantization import Binary, Scalar

SCRATCH = {"lsh": LSH, "ivf": IVF, "hnsw": HNSW, "binary": Binary, "scalar": Scalar, "pq": PQ}


class IndexedTinyVec(TinyVec):
    capabilities = Capabilities(approximate=True, hybrid="application")

    def __init__(self, kind="ivf", oversample=2, filter_policy="adaptive", **settings):
        super().__init__()
        if (
            type(oversample) is not int
            or oversample < 1
            or filter_policy not in ("adaptive", "post", "traverse")
        ):
            raise ValueError(
                "Use a positive integer oversample and adaptive, post, or traverse filtering"
            )
        if kind not in SCRATCH and kind not in {
            "faiss-lsh",
            "faiss-ivf",
            "faiss-hnsw",
            "faiss-ivfpq",
            "usearch",
            "hnswlib",
        }:
            raise ValueError(f"Unknown angular index {kind!r}")
        if filter_policy == "traverse" and kind != "hnsw":
            raise ValueError("Filtered graph traversal needs the teaching HNSW index")
        self.kind = kind
        self.oversample = oversample
        self.filter_policy = filter_policy
        self.settings = settings
        self.index = None

    def create_collection(self, spec):
        if spec.metric != "cosine":
            raise ValueError("Tier 2 indexes use cosine similarity")
        super().create_collection(spec)

    def build(self):
        super().build()
        records = [self._records[key] for key in self._ids]
        self.metadata = MetadataIndex(records)
        self.lexical = BM25(f"{r.text} {r.metadata.get('sku', '')}" for r in records)
        self.index = None
        if not records:
            return
        self.normalized = self._matrix / np.linalg.norm(self._matrix, axis=1, keepdims=True)
        try:
            if self.kind in SCRATCH:
                self.index = SCRATCH[self.kind](self.normalized, **self.settings)
            else:
                from common.stores.native_ann import NativeANN

                self.index = NativeANN(self.normalized, self.kind, **self.settings)
        except Exception:
            # A failed build must be retried or reported on the next query,
            # just as it would be on the first one.
            self._matrix = None
            raise

    def search(self, vector, k=10, filter=None, *, space=None):
        spec = self._require_spec()
        if type(k) is not int or k < 1 or (space is not None and space != spec.space):
            raise ValueError("Invalid k or query embedding space")
        q = checked_vector(vector, spec)
        q /= np.linalg.norm(q)
        expr = parse_filter(filter)
        if self._matrix is None:
            self.build()
        if self.index is None:
            return []
        allowed = self.metadata.eligible(expr) if expr else None
        count = k * self.oversample
        if (
            allowed is not None
            and self.filter_policy == "adaptive"
            and len(allowed) <= max(count, len(self._ids) // 4)
        ):
            rows = sorted(allowed)
        elif allowed is not None and self.filter_policy == "traverse" and self.kind == "hnsw":
            rows = self.index.filtered_candidates(q, count, allowed)
        else:
            rows = self.index.candidates(q, count)
            if allowed is not None:
                rows = [r for r in rows if r in allowed]
        if not len(rows):
            return []
        ranked = sorted(
            zip(rows, (self.normalized[rows] @ q).tolist(), strict=True),
            key=lambda p: (-p[1], p[0]),
        )[:k]
        return [self._hit(int(row), score) for row, score in ranked]

    def _hit(self, row, score):
        key = self._ids[row]
        r = self._records[key]
        return Hit(key, float(score), copy.deepcopy(r.metadata), r.text, float(score))

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        if type(k) is not int or k < 1 or not isinstance(text, str):
            raise ValueError("Hybrid search needs query text and a positive integer k")
        dense = self.search(vector, k * self.oversample, filter, space=space)
        expr = parse_filter(filter)
        eligible = self.metadata.eligible(expr) if expr else None
        lexical = self.lexical.rank(text, eligible, k * self.oversample)
        groups = [[h.id for h in dense], [self._ids[i] for i in lexical]]
        # A literal product identifier has stronger evidence than a rank vote.
        identifier = text.strip().casefold()
        ranked = [
            (
                key,
                score
                + int(
                    bool(identifier)
                    and str(self._records[key].metadata.get("sku", "")).casefold() == identifier
                ),
            )
            for key, score in fuse(groups)
        ]
        ranked.sort(key=lambda row: (-row[1], row[0]))
        return [
            Hit(key, score, copy.deepcopy(self._records[key].metadata), self._records[key].text)
            for key, score in ranked[:k]
        ]

    def snapshot_options(self):
        return {
            "kind": self.kind,
            "oversample": self.oversample,
            "filter_policy": self.filter_policy,
            **self.settings,
        }

    def close(self):
        self.index = None
        super().close()
