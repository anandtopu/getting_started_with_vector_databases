"""Marlowe v5: same-record named vectors and weighted rank fusion across modalities."""

import uuid
from itertools import batched

import numpy as np

from common.stores.types import CollectionSpec, Hit, Record, checked_vector


def weighted_fusion(rankings: dict[str, list[str]], weights: dict[str, float], *, constant=60):
    if (
        set(rankings) != set(weights)
        or constant <= 0
        or any(not np.isfinite(w) or w < 0 for w in weights.values())
        or sum(weights.values()) <= 0
    ):
        raise ValueError("Nonnegative finite weights must cover each branch and sum above zero")
    scores = {}
    for name, ids in rankings.items():
        if weights[name] == 0:
            continue
        for rank, key in enumerate(dict.fromkeys(ids), 1):
            scores[key] = scores.get(key, 0.0) + weights[name] / (constant + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


class MultimodalSearch:
    """Qdrant uses native named vectors. Other engines use explicit separate collections."""

    def __init__(self, database, ids, image_vectors, text_vectors, space: str, metadata=None):
        if (
            len(ids) != len(set(ids))
            or len(ids) != len(image_vectors)
            or np.shape(image_vectors) != np.shape(text_vectors)
        ):
            raise ValueError("Unique aligned image/text rows required")
        self.ids = list(ids)
        self.metadata = metadata or {key: {} for key in ids}
        self.space = space
        self.spec = CollectionSpec("images", np.shape(image_vectors)[1], "cosine", space)
        self.client = database.client
        self.name = "marlowe_photo_" + uuid.uuid4().hex
        self.stores = {}
        for v in [*image_vectors, *text_vectors]:
            checked_vector(v, self.spec)
        if self.client is not None:
            from qdrant_client import models as m

            self.client.create_collection(
                self.name,
                vectors_config={
                    name: m.VectorParams(size=self.spec.dimensions, distance=m.Distance.COSINE)
                    for name in ["image", "text"]
                },
            )
            if ids:
                try:
                    self._put_native(ids, image_vectors, text_vectors)
                except BaseException:
                    self.client.delete_collection(self.name)
                    raise
        else:
            for name, vectors in [("image", image_vectors), ("text", text_vectors)]:
                self.stores[name] = database.collection(
                    "photo_" + name,
                    [
                        Record(key, v, self.metadata[key])
                        for key, v in zip(ids, vectors, strict=True)
                    ],
                    space,
                    dimensions=self.spec.dimensions,
                )

    def _put_native(self, ids, image_vectors, text_vectors):
        from qdrant_client import models as m

        for batch in batched(enumerate(ids), 128):
            self.client.upsert(
                self.name,
                [
                    m.PointStruct(
                        id=i,
                        vector={
                            "image": image_vectors[i].tolist(),
                            "text": text_vectors[i].tolist(),
                        },
                        payload={"product_id": key, **self.metadata[key]},
                    )
                    for i, key in batch
                ],
                wait=True,
            )

    def search(self, vector, *, space, k=10, image_weight=0.7, exclude=()):
        if space != self.space or k < 1 or not 0 <= image_weight <= 1:
            raise ValueError("Use the same SigLIP space, k >= 1 and image_weight in [0, 1]")
        q = checked_vector(vector, self.spec)
        if not self.ids:
            return []
        excluded = set(exclude)
        count = min(len(self.ids), max(5 * k, k + len(excluded)))
        rankings = {}
        for name in ["image", "text"]:
            if self.client is not None:
                points = self.client.query_points(
                    self.name, query=q.tolist(), using=name, limit=count
                ).points
                ids = [p.payload["product_id"] for p in points]
            else:
                ids = [h.id for h in self.stores[name].search(q, count, space=space)]
            rankings[name] = [key for key in ids if key not in excluded]
        ranked = weighted_fusion(rankings, {"image": image_weight, "text": 1 - image_weight})
        return [Hit(key, score, self.metadata[key]) for key, score in ranked[:k]]

    def close(self):
        if self.client is not None:
            self.client.delete_collection(self.name)
