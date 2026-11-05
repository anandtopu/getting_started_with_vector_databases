"""Loopback-only teaching API; one worker, no authentication. Use Marlowe v6 for auth."""

from contextlib import asynccontextmanager
from dataclasses import asdict

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from common.settings import cache_dir
from common.stores.types import CollectionSpec, Record
from tinyvec.durable import DurableTinyVec


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1)
    vector: list[float]
    metadata: dict = Field(default_factory=dict)
    text: str = ""


class Batch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    records: list[Item] = Field(min_length=1, max_length=1000)


class Search(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vector: list[float]
    k: int = Field(default=10, ge=1, le=100)
    filter: dict | None = None
    space: str = "hand-v1"


def create_app(root=None, spec=None):
    @asynccontextmanager
    async def lifespan(app):
        with DurableTinyVec(
            root or cache_dir() / "bonus/service",
            spec or CollectionSpec("service", 2, space="hand-v1"),
        ) as store:
            app.state.store = store
            yield

    app = FastAPI(title="TinyVec durable teaching service", lifespan=lifespan)

    def execute(call):
        try:
            return call()
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post("/records")
    def upsert(body: Batch):
        return execute(
            lambda: {
                "sequence": app.state.store.upsert(
                    [Record(r.id, np.array(r.vector), r.metadata, r.text) for r in body.records]
                )
            }
        )

    @app.delete("/records/{record_id}")
    def delete(record_id: str):
        return execute(lambda: {"sequence": app.state.store.delete([record_id])})

    @app.post("/search")
    def search(body: Search):
        return execute(
            lambda: [
                asdict(h)
                for h in app.state.store.search(body.vector, body.k, body.filter, space=body.space)
            ]
        )

    @app.post("/checkpoint")
    def checkpoint():
        return app.state.store.checkpoint()

    @app.get("/health")
    def health():
        return {"status": "ready", "sequence": app.state.store.wal.sequence}

    return app


app = create_app()
