"""Elasticsearch dense-vector kNN with an IDs prefilter and explicit refresh."""

from elasticsearch import Elasticsearch

from common.settings import setting
from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities
from tinyvec.hybrid import fuse


class ElasticStore(DatabaseStore):
    capabilities = Capabilities(approximate=True, hybrid="application")

    def __init__(self):
        super().__init__()
        self.db = Elasticsearch(
            setting("ELASTICSEARCH_URL", "http://127.0.0.1:9200"), request_timeout=15
        )

    def _create(self, spec):
        self.db.indices.create(
            index=self.name,
            settings={"number_of_shards": 1, "number_of_replicas": 0},
            mappings={
                "properties": {
                    "v": {
                        "type": "dense_vector",
                        "dims": spec.dimensions,
                        "similarity": "cosine",
                        "index": True,
                    },
                    "packed": {"type": "keyword", "index": False, "doc_values": False},
                    "body": {"type": "text"},
                }
            },
        )

    def _put(self, rows):
        ops = []
        for key, r in rows.items():
            ops.extend(
                [
                    {"index": {"_index": self.name, "_id": key}},
                    {"v": r.vector.tolist(), "packed": pack(r), "body": r.text},
                ]
            )
        res = self.db.bulk(operations=ops, refresh=True)
        if res["errors"]:
            raise ValueError(
                f"Elasticsearch bulk failure: {next(i for i in res['items'] if 'error' in i['index'])}"
            )

    def _delete(self, keys):
        self.db.bulk(
            operations=[{"delete": {"_index": self.name, "_id": key}} for key in keys], refresh=True
        )

    def _query(self, q, keys, k):
        knn = {"field": "v", "query_vector": q.tolist(), "k": k, "num_candidates": max(100, k)}
        if keys is not None:
            knn["filter"] = {"ids": {"values": keys}}
        rows = self.db.search(index=self.name, knn=knn, size=k, source=False)["hits"]["hits"]
        return [(r["_id"], 2 * r["_score"] - 1) for r in rows]

    def _payloads(self):
        rows = (
            self.db.mget(index=self.name, ids=list(self.catalog), source_includes=["packed"])[
                "docs"
            ]
            if self.catalog
            else []
        )
        return [r["_source"]["packed"] for r in rows]

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        clause = {"bool": {"must": [{"match": {"body": text}}]}}
        if keys is not None:
            clause["bool"]["filter"] = [{"ids": {"values": keys}}]
        rows = self.db.search(index=self.name, query=clause, size=2 * k, source=False)["hits"][
            "hits"
        ]
        return self.hits(
            fuse([[key for key, _ in self._query(q, keys, 2 * k)], [r["_id"] for r in rows]]), count
        )

    def _drop(self):
        self.db.indices.delete(index=self.name)

    def _disconnect(self):
        self.db.close()
