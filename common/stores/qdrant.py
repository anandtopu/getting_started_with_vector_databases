"""Named dense/sparse vectors and server-side RRF using Qdrant's Query API."""

import hashlib
from collections import Counter
from itertools import batched

from qdrant_client import QdrantClient
from qdrant_client import models as m

from common.settings import setting
from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities
from tinyvec.hybrid import tokens


def sparse(text):
    weights = Counter(
        int.from_bytes(hashlib.blake2s(t.encode(), digest_size=4).digest(), "little")
        for t in tokens(text)
    )
    terms = sorted(weights)
    return m.SparseVector(indices=terms, values=[float(weights[t]) for t in terms])


class QdrantStore(DatabaseStore):
    capabilities = Capabilities(hybrid="native", named_vectors=True, approximate=True)

    def __init__(self, local=False, quantize=False, client=None):
        super().__init__()
        self.owns_client = client is None
        self.db = client or (
            QdrantClient(":memory:")
            if local
            else QdrantClient(url=setting("QDRANT_URL", "http://127.0.0.1:6333"), timeout=20)
        )
        self.quantize = quantize

    def _create(self, spec):
        self.db.create_collection(
            self.name,
            vectors_config={
                "dense": m.VectorParams(size=spec.dimensions, distance=m.Distance.COSINE)
            },
            sparse_vectors_config={"terms": m.SparseVectorParams()},
            quantization_config=m.ScalarQuantization(
                scalar=m.ScalarQuantizationConfig(type=m.ScalarType.INT8)
            )
            if self.quantize
            else None,
        )

    def _put(self, rows):
        # Bound HTTP requests: the full 10k catalog exceeds the server payload limit.
        for batch in batched(rows.items(), 128):
            self.db.upsert(
                self.name,
                points=[
                    m.PointStruct(
                        id=key,
                        vector={
                            "dense": r.vector.tolist(),
                            "terms": sparse(r.text + " " + str(r.metadata.get("sku", ""))),
                        },
                        payload={
                            "body": pack(r),
                            "region": r.metadata.get("region"),
                            "tenant": r.metadata.get("tenant"),
                        },
                    )
                    for key, r in batch
                ],
                wait=True,
            )

    def _delete(self, keys):
        self.db.delete(self.name, points_selector=keys, wait=True)

    def condition(self, keys):
        return None if keys is None else m.Filter(must=[m.HasIdCondition(has_id=keys)])

    def _query(self, q, keys, k):
        pts = self.db.query_points(
            self.name, query=q.tolist(), using="dense", query_filter=self.condition(keys), limit=k
        ).points
        return [(str(p.id), p.score) for p in pts]

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        where = self.condition(keys)
        branches = [m.Prefetch(query=q.tolist(), using="dense", filter=where, limit=k * 2)]
        lexical = sparse(text)
        if lexical.indices:
            branches.append(m.Prefetch(query=lexical, using="terms", filter=where, limit=k * 2))
        pts = self.db.query_points(
            self.name,
            prefetch=branches,
            query=m.FusionQuery(fusion=m.Fusion.RRF),
            query_filter=where,
            limit=count,
        ).points
        return self.hits([(str(p.id), p.score) for p in pts], count)

    def _payloads(self):
        offset = None
        while True:
            points, offset = self.db.scroll(self.name, limit=128, offset=offset, with_payload=True)
            yield from (p.payload["body"] for p in points)
            if offset is None:
                break

    def _drop(self):
        self.db.delete_collection(self.name)

    def _disconnect(self):
        if self.owns_client:
            self.db.close()
