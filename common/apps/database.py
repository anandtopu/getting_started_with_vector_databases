"""One owned application database session, with separate collections per vector space."""

from pathlib import Path
from tempfile import TemporaryDirectory

from common.stores.registry import make_store
from common.stores.types import CollectionSpec, Record


class AppDatabase:
    def __init__(self, backend: str = "tinyvec") -> None:
        self.backend = backend
        self.stores = []
        self.temporary = TemporaryDirectory(prefix="marlowe-app-")
        self.client = None
        if backend == "qdrant-local":
            from qdrant_client import QdrantClient

            self.client = QdrantClient(":memory:")
        elif backend == "qdrant-secure":
            from common.ops.native import open_client

            self.client = open_client()

    def collection(self, name: str, records: list[Record], space: str, dimensions=None):
        if not records and dimensions is None:
            raise ValueError("An empty collection needs explicit dimensions")
        if self.client is not None:
            from common.stores.qdrant import QdrantStore

            store = QdrantStore(client=self.client)
        else:
            # Distinct model spaces may reuse a logical role such as 'products'.
            store = make_store(
                self.backend, path=Path(self.temporary.name) / f"{len(self.stores)}-{name}"
            )
        self.stores.append(store)
        store.create_collection(
            CollectionSpec(name, len(records[0].vector) if records else dimensions, "cosine", space)
        )
        if records:
            store.upsert(records)
        if hasattr(store, "build"):
            store.build()
        return store

    def close(self) -> None:
        try:
            for store in reversed(self.stores):
                store.close()
        finally:
            if self.client is not None:
                self.client.close()
            self.temporary.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
