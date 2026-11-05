"""PostgreSQL cosine search, transaction-safe upsert and native full-text fusion."""

import psycopg

from common.settings import setting
from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities
from tinyvec.hybrid import fuse


class PostgresStore(DatabaseStore):
    capabilities = Capabilities(hybrid="application", approximate=True)

    def __init__(self, index="hnsw"):
        super().__init__()
        if index not in ("flat", "hnsw", "ivfflat"):
            raise ValueError("Choose flat, hnsw or ivfflat")
        self.index_kind = index
        self.db = psycopg.connect(
            setting("POSTGRES_URL", "postgresql://marlowe:marlowe-local@127.0.0.1:5432/marlowe"),
            connect_timeout=5,
            autocommit=True,
        )

    def _create(self, spec):
        self.db.execute("CREATE EXTENSION IF NOT EXISTS vector")
        self.db.execute(
            f"CREATE TABLE {self.name}(key uuid PRIMARY KEY,v vector({spec.dimensions}),payload text,body text)"
        )

    def _put(self, rows):
        with self.db.transaction(), self.db.cursor() as cur:
            cur.executemany(
                f"INSERT INTO {self.name} VALUES (%s,%s::vector,%s,%s) ON CONFLICT(key) DO UPDATE SET v=excluded.v,payload=excluded.payload,body=excluded.body",
                [
                    (
                        key,
                        str(r.vector.tolist()),
                        pack(r),
                        r.text + " " + str(r.metadata.get("sku", "")),
                    )
                    for key, r in rows.items()
                ],
            )

    def build(self):
        if self.index_kind != "flat":
            options = " WITH (lists=8)" if self.index_kind == "ivfflat" else ""
            self.db.execute(
                f"CREATE INDEX IF NOT EXISTS {self.name}_idx ON {self.name} USING {self.index_kind}(v vector_cosine_ops){options}"
            )
        self.db.execute(f"ANALYZE {self.name}")

    def _delete(self, keys):
        self.db.execute(f"DELETE FROM {self.name} WHERE key=ANY(%s::uuid[])", (keys,))

    def _query(self, q, keys, k):
        where = "" if keys is None else "WHERE key=ANY(%s::uuid[])"
        with self.db.transaction():
            self.db.execute("SET LOCAL hnsw.iterative_scan = strict_order")
            rows = self.db.execute(
                f"SELECT key,v <=> %s::vector AS distance FROM {self.name} {where} ORDER BY distance LIMIT %s",
                (str(q.tolist()), *([keys] if keys is not None else []), k),
            ).fetchall()
        return [(str(key), 1 - d) for key, d in rows]

    def hybrid_search(self, text, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        where = "" if keys is None else "AND key=ANY(%s::uuid[])"
        lexical = self.db.execute(
            f"SELECT key FROM {self.name}, plainto_tsquery('simple',%s) t WHERE to_tsvector('simple',body) @@ t {where} ORDER BY ts_rank(to_tsvector('simple',body),t) DESC,key LIMIT %s",
            (text, *([keys] if keys is not None else []), 2 * k),
        ).fetchall()
        dense = self._query(q, keys, 2 * k)
        return self.hits(fuse([[key for key, _ in dense], [str(r[0]) for r in lexical]]), count)

    def _payloads(self):
        return [r[0] for r in self.db.execute(f"SELECT payload FROM {self.name}")]

    def _drop(self):
        self.db.execute(f"DROP TABLE {self.name}")

    def _disconnect(self):
        self.db.close()
