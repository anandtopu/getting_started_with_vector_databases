"""Weaviate v4 collections with explicit vectors, native hybrid ranking and filters."""

import weaviate
from weaviate.classes.config import Configure, DataType, Property, VectorDistances
from weaviate.classes.data import DataObject
from weaviate.classes.query import Filter, MetadataQuery

from common.settings import setting
from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities


class WeaviateStore(DatabaseStore):
    capabilities = Capabilities(hybrid="native", approximate=True)

    def __init__(self, alpha=0.5):
        super().__init__()
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between zero and one")
        self.alpha = alpha
        self.name = "Marlowe" + self.name.split("_")[1]
        self.db = weaviate.connect_to_local(
            host=setting("WEAVIATE_HOST", "127.0.0.1"),
            port=int(setting("WEAVIATE_PORT", "8080")),
            grpc_port=int(setting("WEAVIATE_GRPC_PORT", "50051")),
            skip_init_checks=True,
        )
        if not self.db.is_ready():
            self.db.close()
            raise ConnectionError("The local Weaviate database is not ready")

    def _create(self, spec):
        self.table = self.db.collections.create(
            self.name,
            vector_config=Configure.Vectors.self_provided(
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE
                )
            ),
            properties=[
                Property(name="body", data_type=DataType.TEXT),
                Property(
                    name="packed",
                    data_type=DataType.TEXT,
                    index_searchable=False,
                    index_filterable=False,
                ),
            ],
        )

    def _put(self, rows):
        new = []
        for key, r in rows.items():
            props = {"body": r.text + " " + str(r.metadata.get("sku", "")), "packed": pack(r)}
            if key in self.catalog:
                self.table.data.replace(uuid=key, properties=props, vector=r.vector.tolist())
            else:
                new.append(DataObject(uuid=key, properties=props, vector=r.vector.tolist()))
        if new:
            res = self.table.data.insert_many(new)
            if res.has_errors:
                raise RuntimeError(f"Weaviate insert failed: {res.errors}")

    def _delete(self, keys):
        for key in keys:
            self.table.data.delete_by_id(key)

    def condition(self, keys):
        return None if keys is None else Filter.by_id().contains_any(keys)

    def _query(self, q, keys, k):
        res = self.table.query.near_vector(
            q.tolist(),
            filters=self.condition(keys),
            limit=k,
            return_properties=[],
            return_metadata=MetadataQuery(distance=True),
        )
        return [(str(obj.uuid), 1 - obj.metadata.distance) for obj in res.objects]

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        res = self.table.query.hybrid(
            query=text,
            vector=q.tolist(),
            alpha=self.alpha,
            query_properties=["body"],
            filters=self.condition(keys),
            limit=count,
            return_metadata=MetadataQuery(score=True),
        )
        return self.hits([(str(o.uuid), float(o.metadata.score)) for o in res.objects], count)

    def _payloads(self):
        return (
            obj.properties["packed"] for obj in self.table.iterator(return_properties=["packed"])
        )

    def _drop(self):
        self.db.collections.delete(self.name)

    def _disconnect(self):
        self.db.close()
