"""DuckDB native fixed-size array cosine scan with parameterized SQL."""

import duckdb

from common.stores.database import DatabaseStore, pack


class DuckStore(DatabaseStore):
    def __init__(self, path):
        super().__init__()
        self.db = duckdb.connect(
            str(path),
            config={"autoinstall_known_extensions": False, "autoload_known_extensions": False},
        )

    def _create(self, spec):
        self.db.execute(
            f"CREATE TABLE {self.name}(key UUID PRIMARY KEY, v FLOAT[{spec.dimensions}], payload VARCHAR)"
        )

    def _put(self, rows):
        self.db.begin()
        try:
            self.db.executemany(
                f"INSERT OR REPLACE INTO {self.name} VALUES (?,?,?)",
                [(key, r.vector.tolist(), pack(r)) for key, r in rows.items()],
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _delete(self, keys):
        self.db.execute(f"DELETE FROM {self.name} WHERE key IN (SELECT UNNEST(?::UUID[]))", [keys])

    def _query(self, q, keys, k):
        where = "" if keys is None else "WHERE key IN (SELECT UNNEST(?::UUID[]))"
        rows = self.db.execute(
            f"SELECT key,array_cosine_similarity(v,?::FLOAT[{self.spec.dimensions}]) AS score FROM {self.name} {where} ORDER BY score DESC,key LIMIT ?",
            [q.tolist(), *([keys] if keys is not None else []), k],
        ).fetchall()
        return [(str(key), score) for key, score in rows]

    def _payloads(self):
        return [r[0] for r in self.db.execute(f"SELECT payload FROM {self.name}").fetchall()]

    def _drop(self):
        self.db.execute(f"DROP TABLE {self.name}")

    def _disconnect(self):
        self.db.close()
