"""Factories expose only implemented adapters, with actionable optional-install errors."""

from importlib import import_module
from pathlib import Path

from common.errors import CourseError

DATABASES = {
    "chroma": ("chroma", "ChromaStore", "embedded"),
    "lancedb": ("lancedb", "LanceStore", "embedded"),
    "duckdb": ("duckdb", "DuckStore", "embedded"),
    "pgvector": ("pgvector", "PostgresStore", "pgvector"),
    "qdrant": ("qdrant", "QdrantStore", "qdrant"),
    "weaviate": ("weaviate", "WeaviateStore", "weaviate"),
    "milvus": ("milvus", "MilvusStore", "milvus"),
    "elasticsearch": ("elasticsearch", "ElasticStore", "landscape"),
    "redis": ("redis", "RedisStore", "landscape"),
    "mongodb": ("mongodb", "MongoStore", "landscape"),
    "vespa": ("vespa", "VespaStore", "landscape"),
}


def make_store(backend: str = "tinyvec", *, path: Path | None = None, **parameters: object):
    if backend in DATABASES:
        module, cls, extra = DATABASES[backend]
        try:
            factory = getattr(import_module(f"common.stores.{module}"), cls)
        except ImportError as exc:
            raise CourseError(f"Install --extra {extra} for {backend}: {exc}") from exc
        if backend in {"chroma", "lancedb", "duckdb"}:
            if path is None:
                raise ValueError(f"Provide a unique local database path for {backend}")
            return factory(path, **parameters)
        return factory(**parameters)
    if backend == "tinyvec":
        from tinyvec import TinyVec

        return TinyVec(**parameters)
    if backend == "sqlite-vec":
        from common.stores.sqlite_vec import SQLiteVecStore

        return SQLiteVecStore(path)
    if backend == "faiss-flat":
        from common.stores.faiss_flat import FaissFlatStore

        return FaissFlatStore(**parameters)
    if backend == "ann":
        from common.stores.ann import IndexedTinyVec

        return IndexedTinyVec(**parameters)
    raise CourseError(
        f"Unknown backend {backend!r}. Choose tinyvec, sqlite-vec, faiss-flat, or ann."
    )
