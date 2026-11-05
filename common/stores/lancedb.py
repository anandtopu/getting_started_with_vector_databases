"""LanceDB table with transactional merge, explicit Arrow vectors and prefilter."""

import lancedb
import pyarrow as pa
from lancedb.index import FTS

from common.stores.database import DatabaseStore, literals, pack
from common.stores.types import Capabilities


class LanceStore(DatabaseStore):
    capabilities = Capabilities(hybrid="native")

    def __init__(self, path):
        super().__init__()
        self.db = lancedb.connect(str(path))

    def _create(self, spec):
        self.schema = pa.schema(
            [
                ("key", pa.string()),
                ("vector", pa.list_(pa.float32(), spec.dimensions)),
                ("payload", pa.string()),
                ("body", pa.string()),
            ]
        )
        self.fts_ready = False
        self.table = self.db.create_table(self.name, schema=self.schema)

    def _put(self, rows):
        data = pa.Table.from_pylist(
            [
                {
                    "key": key,
                    "vector": r.vector.tolist(),
                    "payload": pack(r),
                    "body": r.text + " " + str(r.metadata.get("sku", "")),
                }
                for key, r in rows.items()
            ],
            schema=self.schema,
        )
        self.table.merge_insert(
            "key"
        ).when_matched_update_all().when_not_matched_insert_all().execute(data)

    def _delete(self, keys):
        self.table.delete(f"key IN ({literals(keys)})")

    def _query(self, q, keys, k):
        search = self.table.search(q).distance_type("cosine")
        if keys is not None:
            search = search.where(f"key IN ({literals(keys)})", prefilter=True)
        return [
            (r["key"], 1 - r["_distance"])
            for r in search.select(["key", "_distance"]).limit(k).to_list()
        ]

    def _payloads(self):
        return self.table.to_arrow()["payload"].to_pylist()

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        if not self.fts_ready:
            self.table.create_index("body", config=FTS())
            self.fts_ready = True
        query = (
            self.table.search(query_type="hybrid", vector_column_name="vector", fts_columns="body")
            .vector(q)
            .text(text)
        )
        if keys is not None:
            query = query.where(f"key IN ({literals(keys)})", prefilter=True)
        return self.hits(
            [(r["key"], r["_relevance_score"]) for r in query.limit(count).to_list()], count
        )

    def _drop(self):
        self.db.drop_table(self.name)

    def _disconnect(self):
        self.db.close()
