"""Local Marlowe v5 API. Run: uv run --extra apps uvicorn common.apps.marlowe_api:app
Bind to loopback. Authentication and production operations are taught in Tier 5.
"""

from contextlib import asynccontextmanager
from dataclasses import asdict
from threading import RLock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from common.apps.marlowe import MarloweSearch
from common.errors import CourseError
from common.settings import setting


class SearchRequest(BaseModel):
    multilingual: bool = False
    query_id: str = "q000"
    text: str | None = Field(default=None, max_length=2000)
    k: int = Field(default=5, ge=1, le=30)
    filter: dict | None = None


class HelpRequest(BaseModel):
    question_id: str = "rag-000"
    text: str | None = Field(default=None, max_length=2000)
    generate: bool = False


class PhotoRequest(BaseModel):
    product_id: str = "p0000000"
    text: str | None = Field(default=None, max_length=2000)
    k: int = Field(default=5, ge=1, le=30)
    image_weight: float = Field(default=0.7, ge=0, le=1)


class DuplicateRequest(BaseModel):
    first: str
    second: str
    threshold: float = Field(ge=-1, le=1)


def create_app(backend=None, limit=1000):
    lock = RLock()

    @asynccontextmanager
    async def lifespan(app):
        app.state.service = MarloweSearch(backend or setting("APP_BACKEND", "tinyvec"), limit)
        try:
            yield
        finally:
            app.state.service.close()

    app = FastAPI(title="Marlowe Search v5", lifespan=lifespan)

    def call(method, **kwargs):
        with lock:
            try:
                return getattr(app.state.service, method)(**kwargs)
            except ValueError as exc:
                raise HTTPException(400, str(exc)) from exc
            except CourseError as exc:
                raise HTTPException(503, str(exc)) from exc

    @app.get("/health")
    def health():
        return {"status": "ready", "version": 5, "backend": app.state.service.database.backend}

    @app.post("/search")
    def search(request: SearchRequest):
        return asdict(call("search", **request.model_dump()))

    @app.post("/help")
    def help_center(request: HelpRequest):
        return call("help", **request.model_dump())

    @app.get("/similar/{product_id}")
    def similar(product_id: str):
        return call("similar", product_id=product_id)

    @app.post("/duplicates")
    def duplicates(request: DuplicateRequest):
        return call("duplicate", **request.model_dump())

    @app.post("/photos")
    def photos(request: PhotoRequest):
        return call("photo", **request.model_dump())

    return app


app = create_app()
