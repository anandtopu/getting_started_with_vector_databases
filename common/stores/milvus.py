"""MilvusClient explicit schema, index parameters and consistency selection."""

from pymilvus import AnnSearchRequest, DataType, Function, FunctionType, MilvusClient, RRFRanker

from common.settings import setting
from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities


class MilvusStore(DatabaseStore):
    capabilities = Capabilities(hybrid="native", named_vectors=True, approximate=True)

    def __init__(self, index="HNSW", consistency="Strong"):
        super().__init__()
        if index not in {"FLAT", "HNSW", "IVF_FLAT", "DISKANN"} or consistency not in {
            "Strong",
            "Session",
            "Bounded",
            "Eventually",
        }:
            raise ValueError("Invalid index or consistency")
        self.kind = index
        self.consistency = consistency
        self.db = MilvusClient(uri=setting("MILVUS_URL", "http://127.0.0.1:19530"), timeout=20)

    def _create(self, spec):
        schema = self.db.create_schema(auto_id=False, enable_dynamic_field=False)
        schema.add_field("key", DataType.VARCHAR, is_primary=True, max_length=64)
        schema.add_field("v", DataType.FLOAT_VECTOR, dim=spec.dimensions)
        schema.add_field("packed", DataType.VARCHAR, max_length=65535)
        schema.add_field("body", DataType.VARCHAR, max_length=65535, enable_analyzer=True)
        schema.add_field("terms", DataType.SPARSE_FLOAT_VECTOR)
        schema.add_function(
            Function(
                name="lexical",
                input_field_names=["body"],
                output_field_names=["terms"],
                function_type=FunctionType.BM25,
            )
        )
        idx = self.db.prepare_index_params()
        params = {"HNSW": {"M": 16, "efConstruction": 80}, "IVF_FLAT": {"nlist": 8}}.get(
            self.kind, {}
        )
        idx.add_index(field_name="v", index_type=self.kind, metric_type="COSINE", params=params)
        idx.add_index(field_name="terms", index_type="SPARSE_INVERTED_INDEX", metric_type="BM25")
        self.db.create_collection(
            self.name, schema=schema, index_params=idx, consistency_level=self.consistency
        )

    def _put(self, rows):
        self.db.upsert(
            self.name,
            data=[
                {
                    "key": key,
                    "v": r.vector.tolist(),
                    "packed": pack(r),
                    "body": r.text + " " + str(r.metadata.get("sku", "")),
                }
                for key, r in rows.items()
            ],
        )

    def build(self):
        self.db.flush(self.name)

    def _delete(self, keys):
        self.db.delete(self.name, ids=keys)

    def _query(self, q, keys, k):
        expression = "" if keys is None else "key in " + str(keys)
        params = {"HNSW": {"ef": max(64, k)}, "IVF_FLAT": {"nprobe": 8}}.get(self.kind, {})
        res = self.db.search(
            self.name,
            data=[q.tolist()],
            anns_field="v",
            limit=k,
            filter=expression,
            search_params={"metric_type": "COSINE", "params": params},
            consistency_level=self.consistency,
        )
        return [(str(p["key"]), float(p["distance"])) for p in res[0]]

    def _payloads(self):
        it = self.db.query_iterator(
            self.name, output_fields=["packed"], batch_size=256, consistency_level="Strong"
        )
        try:
            while batch := it.next():
                yield from (r["packed"] for r in batch)
        finally:
            it.close()

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        expr = None if keys is None else "key in " + str(keys)
        requests = [
            AnnSearchRequest(
                [q.tolist()], "v", {"metric_type": "COSINE", "params": {}}, limit=2 * k, expr=expr
            ),
            AnnSearchRequest(
                [text], "terms", {"metric_type": "BM25", "params": {}}, limit=2 * k, expr=expr
            ),
        ]
        rows = self.db.hybrid_search(
            self.name,
            reqs=requests,
            ranker=RRFRanker(),
            limit=count,
            consistency_level=self.consistency,
        )
        return self.hits([(str(r["key"]), r["distance"]) for r in rows[0]], count)

    def _drop(self):
        self.db.drop_collection(self.name)

    def _disconnect(self):
        self.db.close()
