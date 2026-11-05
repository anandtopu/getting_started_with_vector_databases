"""SQLite-vec exact scalar search with validated, parameterized metadata filters.

This foundation adapter deliberately uses full scans, not an ANN index. SQLite
owns persistence and cosine/L2 scoring; dot product is a registered NumPy UDF.
"""

import json
import sqlite3
import threading
from collections.abc import Iterable
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

import numpy as np

from common.errors import CourseError
from common.io import canonical_json
from common.stores.filters import Filter, parse_filter
from common.stores.types import (
    Capabilities,
    CollectionSpec,
    Hit,
    Record,
    checked_record,
    checked_vector,
)


def filter_sql(expression: Filter | None) -> tuple[str, list]:
    if expression is None:
        return "1", []
    if expression.op in {"and", "or"}:
        children = [filter_sql(child) for child in expression.clauses]
        return "(" + f" {expression.op.upper()} ".join(sql for sql, _ in children) + ")", [
            value for _, values in children for value in values
        ]
    path = "$." + json.dumps(expression.field)
    if expression.op == "in":
        children = [
            filter_sql(Filter(op="eq", field=expression.field, value=value))
            for value in expression.value
        ]
        return "(" + " OR ".join(sql for sql, _ in children) + ")" if children else "0", [
            v for _, values in children for v in values
        ]
    if expression.op == "eq":
        kind = {
            str: "text",
            int: "integer",
            float: "real",
            bool: "true" if expression.value else "false",
            type(None): "null",
        }.get(type(expression.value))
        if kind is None:
            raise ValueError("SQLite filters require JSON scalar comparison values")
        return "(json_type(metadata, ?) = ? AND json_extract(metadata, ?) IS ?)", [
            path,
            kind,
            path,
            expression.value,
        ]
    operator = {"lt": "<", "lte": "<=", "gt": ">", "gte": ">="}[expression.op]
    return (
        f"(json_type(metadata, ?) IN ('integer', 'real') AND json_extract(metadata, ?) {operator} ?)",
        [path, path, expression.value],
    )


class SQLiteVecStore:
    capabilities = Capabilities()

    def __init__(self, path: Path | None = None) -> None:
        try:
            import sqlite_vec
        except ImportError as exc:
            raise CourseError("Install embedded databases: uv sync --extra embedded") from exc
        if path is not None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(
            str(path) if path else ":memory:", check_same_thread=False
        )
        self._lock = threading.RLock()
        self._connection.enable_load_extension(True)
        try:
            sqlite_vec.load(self._connection)
        finally:
            self._connection.enable_load_extension(False)
        self._connection.create_function(
            "marlowe_dot",
            2,
            lambda a, b: float(
                np.frombuffer(a, dtype=np.float32) @ np.frombuffer(b, dtype=np.float32)
            ),
            deterministic=True,
        )
        self._connection.execute("CREATE TABLE IF NOT EXISTS collection (spec TEXT NOT NULL)")
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS records (id TEXT PRIMARY KEY, vector BLOB NOT NULL, metadata TEXT NOT NULL, text TEXT NOT NULL)"
        )
        row = self._connection.execute("SELECT spec FROM collection").fetchone()
        self.spec = CollectionSpec(**json.loads(row[0])) if row else None
        self._connection.commit()

    def create_collection(self, spec: CollectionSpec) -> None:
        with self._lock:
            if self.spec is not None and self.spec != spec:
                raise ValueError("Collection already exists with a different schema")
            if self.spec is None:
                self._connection.execute(
                    "INSERT INTO collection VALUES (?)", (canonical_json(asdict(spec)),)
                )
                self._connection.commit()
            self.spec = spec

    def _require_spec(self) -> CollectionSpec:
        if self.spec is None:
            raise ValueError("Create a collection before using the store")
        return self.spec

    def upsert(self, records: Iterable[Record]) -> None:
        rows = [checked_record(record, self._require_spec()) for record in records]
        with self._lock, self._connection:
            self._connection.executemany(
                "INSERT INTO records VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET vector=excluded.vector, metadata=excluded.metadata, text=excluded.text",
                [(r.id, r.vector.tobytes(), canonical_json(r.metadata), r.text) for r in rows],
            )

    def delete(self, ids: Iterable[str]) -> None:
        self._require_spec()
        with self._lock, self._connection:
            self._connection.executemany(
                "DELETE FROM records WHERE id = ?", [(key,) for key in ids]
            )

    def search(
        self,
        vector: object,
        k: int = 10,
        filter: Filter | dict | None = None,
        *,
        space: str | None = None,
    ) -> list[Hit]:
        spec = self._require_spec()
        if isinstance(k, bool) or not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        if space is not None and space != spec.space:
            raise ValueError("Query embedding space does not match this collection")
        query = checked_vector(vector, spec)
        condition, parameters = filter_sql(parse_filter(filter))
        scoring = {
            "cosine": "1 - vec_distance_cosine(vector, ?)",
            "l2": "-vec_distance_L2(vector, ?)",
            "dot": "marlowe_dot(vector, ?)",
        }[spec.metric]
        with self._lock:
            rows = self._connection.execute(
                f"SELECT id, {scoring} AS score, metadata, text FROM records WHERE {condition} ORDER BY score DESC, id ASC LIMIT ?",
                [query.tobytes(), *parameters, k],
            ).fetchall()
        return [
            Hit(key, float(score), json.loads(metadata), text, float(score))
            for key, score, metadata, text in rows
        ]

    def hybrid_search(self, *args: object, **kwargs: object) -> list[Hit]:
        raise CourseError(
            "The foundation SQLite adapter supports exact vector search; hybrid arrives in Tier 2."
        )

    def save(self, path: Path) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)
        with self._lock, closing(sqlite3.connect(Path(path) / "snapshot.db")) as destination:
            self._connection.backup(destination)

    def records(self) -> list[Record]:
        self._require_spec()
        with self._lock:
            rows = self._connection.execute(
                "SELECT id, vector, metadata, text FROM records ORDER BY id"
            ).fetchall()
        return [
            Record(key, np.frombuffer(vector, dtype=np.float32).copy(), json.loads(metadata), text)
            for key, vector, metadata, text in rows
        ]

    def close(self) -> None:
        self._connection.close()
