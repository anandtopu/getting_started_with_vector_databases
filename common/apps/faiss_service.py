"""FAISS behind a local FastAPI contract; one process owns the records and snapshots.
Run: uv run --extra libs --extra apps uvicorn common.apps.faiss_service:app --host 127.0.0.1
"""

from contextlib import asynccontextmanager
from threading import RLock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from common.settings import cache_dir
from common.stores.faiss_flat import FaissFlatStore
from common.stores.types import CollectionSpec, Record


class Item(BaseModel):
    id: str
    vector: list[float]
    metadata: dict = Field(default_factory=dict)
    text: str = ""


class Query(BaseModel):
    vector: list[float]
    k: int = Field(5, ge=1, le=100)
    filter: dict | None = None
    space: str


def create_app(path, dimensions=384, space="marlowe-service"):
    lock = RLock()

    @asynccontextmanager
    async def lifespan(app):
        store = FaissFlatStore.load(path) if (path / "snapshot.json").exists() else FaissFlatStore()
        store.create_collection(CollectionSpec("service", dimensions, "cosine", space))
        app.state.store = store
        try:
            yield
        finally:
            store.close()

    api = FastAPI(lifespan=lifespan)

    @api.put("/items")
    def put(items: list[Item]):
        with lock:
            try:
                api.state.store.upsert(Record(**i.model_dump()) for i in items)
            except ValueError as error:
                raise HTTPException(422, str(error)) from error
            return {"upserted": len(items)}

    @api.post("/search")
    def search(query: Query):
        with lock:
            try:
                rows = api.state.store.search(
                    query.vector, query.k, query.filter, space=query.space
                )
            except ValueError as error:
                raise HTTPException(422, str(error)) from error
            return [{"id": r.id, "score": r.score, "metadata": r.metadata} for r in rows]

    @api.delete("/items/{key}")
    def delete(key: str):
        with lock:
            api.state.store.delete([key])
        return {"deleted": key}

    @api.post("/snapshot")
    def save():
        with lock:
            api.state.store.save(path)
        return {"saved": True}

    return api


app = create_app(cache_dir() / "tier3/faiss-service")
