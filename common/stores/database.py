"""Shared lifecycle for isolated teaching collections with native cosine retrieval.

The portable predicate is evaluated on a session metadata catalog; eligible keys
are passed into the native query before its limit. Native examples show the
engine's own field predicates. Snapshots read the stored payloads back from the DB.
"""

import copy
import json
import uuid
from pathlib import Path

import numpy as np

from common.errors import CourseError
from common.io import canonical_json
from common.stores.filters import matches, parse_filter
from common.stores.types import Capabilities, Hit, Record, checked_record, checked_vector
from tinyvec import TinyVec


def token(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "marlowe/course/" + key))


def pack(row):
    return canonical_json(
        {"id": row.id, "metadata": row.metadata, "text": row.text, "vector": row.vector.tolist()}
    )


def unpack(value):
    body = json.loads(value)
    return Record(
        body["id"], np.asarray(body["vector"], dtype=np.float32), body["metadata"], body["text"]
    )


def literals(keys):
    # Only UUIDs produced by token() reach a native IN list.
    return ",".join("'" + str(uuid.UUID(k)) + "'" for k in keys)


class DatabaseStore:
    capabilities = Capabilities()

    def __init__(self):
        self.spec = None
        self.name = "marlowe_" + uuid.uuid4().hex
        self.catalog = {}
        self.created = False
        self.write_uncertain = False

    def _require_confirmed(self):
        if self.write_uncertain:
            raise CourseError(
                "A native write failed and may have partially applied. Close this private session and restore a known snapshot into a fresh collection."
            )

    def _mutate(self, operation, values):
        self._require_confirmed()
        try:
            operation(values)
        except Exception:
            self.write_uncertain = True
            raise

    def create_collection(self, spec):
        if spec.metric != "cosine":
            raise ValueError("Tier 3 comparison collections use cosine")
        if self.spec is not None:
            if self.spec != spec:
                raise ValueError("Collection already has a different schema")
            return
        self._create(spec)
        self.spec = spec
        self.created = True

    def upsert(self, records):
        self._require_confirmed()
        if self.spec is None:
            raise ValueError("Create a collection first")
        rows = {}
        for record in records:
            row = checked_record(record, self.spec)
            rows[token(row.id)] = row
        if rows:
            self._mutate(self._put, rows)
            self.catalog.update({key: (r.id, r.metadata, r.text) for key, r in rows.items()})

    def delete(self, ids):
        self._require_confirmed()
        keys = [token(i) for i in ids if token(i) in self.catalog]
        if keys:
            self._mutate(self._delete, keys)
            for key in keys:
                self.catalog.pop(key, None)

    def request(self, vector, k, expression, space):
        self._require_confirmed()
        if self.spec is None or type(k) is not int or k < 1:
            raise ValueError("Create the collection and supply positive integer k")
        if space is not None and self.spec.space != space:
            raise ValueError("Query embedding space mismatch")
        q = checked_vector(vector, self.spec)
        expr = parse_filter(expression)
        keys = (
            None
            if expr is None
            else [key for key, (_, metadata, _) in self.catalog.items() if matches(metadata, expr)]
        )
        return q, keys, min(k, len(self.catalog) if keys is None else len(keys))

    def hits(self, pairs, k):
        ordered = sorted(pairs, key=lambda p: (-p[1], self.catalog[p[0]][0]))[:k]
        return [
            Hit(
                self.catalog[key][0],
                float(score),
                copy.deepcopy(self.catalog[key][1]),
                self.catalog[key][2],
                float(score),
            )
            for key, score in ordered
        ]

    def search(self, vector, k=10, filter=None, *, space=None):
        q, keys, count = self.request(vector, k, filter, space)
        if not count:
            return []
        return self.hits(self._query(q, keys, count), count)

    def hybrid_search(self, *args, **kwargs):
        raise CourseError(
            "This adapter exposes vector retrieval; see the module's native hybrid example"
        )

    def save(self, path: Path):
        self._require_confirmed()
        if self.spec is None:
            raise ValueError("Create the collection first")
        snapshot = TinyVec()
        snapshot.create_collection(self.spec)
        rows = [unpack(payload) for payload in self._payloads()]
        if {token(r.id) for r in rows} != set(self.catalog):
            raise ValueError("Snapshot did not read all stored records")
        snapshot.upsert(rows)
        snapshot.save(path)

    def restore(self, path):
        snapshot = TinyVec.load(path)
        self.create_collection(snapshot.spec)
        self.upsert(snapshot.records())
        return self

    def close(self):
        try:
            if self.created:
                self._drop()
                self.created = False
        finally:
            self._disconnect()
