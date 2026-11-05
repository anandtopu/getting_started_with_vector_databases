"""Authenticated local Marlowe v6. Launch with scripts/serve_tier5.py for verified TLS."""

import time
import uuid
from contextlib import asynccontextmanager
from threading import BoundedSemaphore

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from common.apps.secure_market import SecureMarket
from common.security.audit import AuditLog
from common.security.identity import Keyring
from common.settings import cache_dir, setting


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Search(StrictModel):
    query_id: str = "q000"
    text: str | None = Field(None, max_length=2000)
    k: int = Field(5, ge=1, le=30)
    filter: dict | None = None
    multilingual: bool = False


class Help(StrictModel):
    question_id: str = "rag-000"
    text: str | None = Field(None, max_length=2000)
    generate: bool = False


class Photo(StrictModel):
    product_id: str = "p0000000"
    text: str | None = Field(None, max_length=2000)
    k: int = Field(5, ge=1, le=30)
    image_weight: float = Field(0.7, ge=0, le=1)


class Duplicate(StrictModel):
    first: str
    second: str
    threshold: float = Field(ge=-1, le=1)


def create_app(*, keyring=None, root=None, backend=None, limit=1000, in_flight=4):
    directory = root or cache_dir() / "tier5/service"
    registry = CollectorRegistry()
    requests = Counter(
        "marlowe_requests_total", "Completed HTTP requests", ["route", "status"], registry=registry
    )
    duration = Histogram(
        "marlowe_request_seconds", "End-to-end request time", ["route"], registry=registry
    )
    active = Gauge("marlowe_in_flight", "Admitted application operations", registry=registry)
    rejected = Counter("marlowe_rejected_total", "Admission limit rejections", registry=registry)
    slots = BoundedSemaphore(in_flight)
    bearer = HTTPBearer(auto_error=False)
    bearer_dependency = Depends(bearer)
    audit = AuditLog(directory / "audit.jsonl")

    @asynccontextmanager
    async def lifespan(app):
        from pathlib import Path

        app.state.keys = keyring or Keyring.from_file(
            Path(setting("AUTH_FILE", str(cache_dir() / "tier5/runtime/identities.json")))
        )
        app.state.market = SecureMarket(
            directory, backend or setting("APP_BACKEND", "tinyvec"), limit
        )
        try:
            yield
        finally:
            app.state.market.close()

    app = FastAPI(title="Marlowe Search v6", lifespan=lifespan)

    def identity(
        request: Request, credentials: HTTPAuthorizationCredentials | None = bearer_dependency
    ):
        try:
            if credentials is None:
                raise PermissionError()
            principal = app.state.keys.authenticate(credentials.credentials)
            request.state.principal = principal
            return principal
        except PermissionError as exc:
            raise HTTPException(
                401, "Valid bearer credentials required", headers={"WWW-Authenticate": "Bearer"}
            ) from exc

    @app.middleware("http")
    async def observe(request, call_next):
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            route = getattr(request.scope.get("route"), "path", "unmatched")
            principal = getattr(request.state, "principal", None)
            await run_in_threadpool(
                audit.record,
                subject=principal.subject if principal else "anonymous",
                tenant=principal.tenant if principal else "",
                action=route,
                outcome=str(status),
                request_id=uuid.uuid4().hex,
            )
            requests.labels(route, str(status)).inc()
            duration.labels(route).observe(time.perf_counter() - start)

    def call(principal, method, **kwargs):
        if not slots.acquire(blocking=False):
            rejected.inc()
            raise HTTPException(429, "Busy; retry with backoff", headers={"Retry-After": "1"})
        active.inc()
        try:
            market = app.state.market
            return (
                market.call(principal, method, kwargs)
                if method in {"search", "help", "similar", "duplicate", "photo"}
                else getattr(market, method)(principal, **kwargs)
            )
        except PermissionError as exc:
            raise HTTPException(403, str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(404, "Listing unavailable") from exc
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        finally:
            active.dec()
            slots.release()

    identity_dependency = Depends(identity)

    @app.get("/health")
    def health():
        return {"status": "ready", "version": 6}

    @app.post("/search")
    def search(body: Search, principal=identity_dependency):
        return call(principal, "search", **body.model_dump())

    @app.post("/help")
    def help_center(body: Help, principal=identity_dependency):
        return call(principal, "help", **body.model_dump())

    @app.post("/photos")
    def photos(body: Photo, principal=identity_dependency):
        return call(principal, "photo", **body.model_dump())

    @app.get("/similar/{record_id}")
    def similar(record_id: str, principal=identity_dependency):
        return call(principal, "similar", product_id=record_id)

    @app.post("/duplicates")
    def duplicates(body: Duplicate, principal=identity_dependency):
        return call(principal, "duplicate", **body.model_dump())

    @app.delete("/listings/{record_id}")
    def delete(record_id: str, principal=identity_dependency):
        return call(principal, "delete", record_id=record_id)

    @app.post("/ops/backup")
    def backup(principal=identity_dependency):
        return call(principal, "backup")

    @app.get("/metrics")
    def metrics(principal=identity_dependency):
        if not principal.permits("admin"):
            raise HTTPException(403, "Administrator role required")
        return Response(generate_latest(registry), media_type="text/plain; version=0.0.4")

    return app


app = create_app()
