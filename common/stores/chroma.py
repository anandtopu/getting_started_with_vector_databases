"""Persistent Chroma with user-provided vectors and a course-owned collection."""

import chromadb

from common.stores.database import DatabaseStore, pack
from common.stores.types import Capabilities


class ChromaStore(DatabaseStore):
    capabilities = Capabilities(approximate=True)

    def __init__(self, path):
        super().__init__()
        self.db = chromadb.PersistentClient(
            path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
        )

    def _create(self, spec):
        self.table = self.db.create_collection(
            self.name,
            embedding_function=None,
            configuration={"hnsw": {"space": "cosine", "num_threads": 1}},
        )

    def _put(self, rows):
        self.table.upsert(
            ids=list(rows),
            embeddings=[r.vector.tolist() for r in rows.values()],
            documents=[pack(r) for r in rows.values()],
        )

    def _delete(self, keys):
        self.table.delete(ids=keys)

    def _query(self, q, keys, k):
        result = self.table.query(
            query_embeddings=[q.tolist()], ids=keys, n_results=k, include=["distances"]
        )
        return [
            (key, 1 - distance)
            for key, distance in zip(result["ids"][0], result["distances"][0], strict=True)
        ]

    def _payloads(self):
        return self.table.get(include=["documents"])["documents"]

    def _drop(self):
        self.db.delete_collection(self.name)

    def _disconnect(self):
        self.table = None
        self.db.close()
        self.db = None
