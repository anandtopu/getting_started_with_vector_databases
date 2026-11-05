"""Strict configs reject typos instead of silently running a different experiment."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class BenchConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    backend: Literal[
        "tinyvec",
        "sqlite-vec",
        "faiss-flat",
        "ann",
        "chroma",
        "lancedb",
        "duckdb",
        "pgvector",
        "qdrant",
        "weaviate",
        "milvus",
        "elasticsearch",
        "redis",
        "mongodb",
        "vespa",
    ] = "tinyvec"
    retrieval: Literal["vector", "hybrid"] = "vector"
    dataset: Literal["fixture", "catalog"] = "fixture"
    metric: Literal["cosine", "dot", "l2"] = "cosine"
    limit: int = Field(default=1000, ge=20)
    k: int = Field(default=10, ge=1)
    warmup: int = Field(default=20, ge=0)
    repetitions: int = Field(default=5, ge=1)
    queries: int = Field(default=100, ge=1)
    seed: int = 20261104
    threads: int = Field(default=1, ge=1)
    split: Literal["all", "development", "test"] = "test"
    query_types: list[Literal["semantic", "keyword", "filtered", "misspelled", "multilingual"]] = (
        Field(
            default_factory=lambda: [
                "semantic",
                "keyword",
                "filtered",
                "misspelled",
                "multilingual",
            ]
        )
    )
    parameters: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_backend_threads(self):
        if self.retrieval == "hybrid" and self.backend not in {
            "ann",
            "lancedb",
            "pgvector",
            "qdrant",
            "weaviate",
            "milvus",
            "elasticsearch",
            "redis",
        }:
            raise ValueError("Choose an adapter with hybrid retrieval")
        if self.backend in ("faiss-flat", "ann") and self.threads != 1:
            raise ValueError("The teaching FAISS adapter uses one thread; set threads: 1")
        return self


def load_config(path: Path) -> BenchConfig:
    return BenchConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
