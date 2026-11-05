"""Small shared fixtures and evidence records; lesson algorithms stay in their scripts."""

import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from common.bench.hardware import hardware, provenance
from common.data import load_products, load_vectors
from common.embeddings import frozen_query
from common.io import atomic_json, file_hash
from common.settings import ROOT, cache_dir, data_dir
from common.stores.types import Hit


def catalog(limit: int = 1000):
    products = load_products(limit=limit)
    vectors, metadata = load_vectors(data_dir() / "embeddings_10k.parquet", products)
    query, query_meta = frozen_query("q000", data_dir())
    if metadata["space"] != query_meta["space"]:
        raise ValueError("Mismatched frozen spaces")
    return products, vectors, query, metadata


def hand_features() -> tuple[list[str], np.ndarray, np.ndarray]:
    # Coordinates are explicitly designed: warmth and portability, on a 0–1 scale.
    return (
        ["mug-warmer", "travel-flask", "reading-chair", "desk-lamp"],
        np.array([[1.0, 0.2], [0.8, 1.0], [0.1, 0.0], [0.0, 0.2]], dtype=np.float32),
        np.array([1.0, 0.1], dtype=np.float32),
    )


def ranked_hits(products, ranked: list[tuple[str, float]]) -> list[Hit]:
    rows = products.set_index("id").to_dict(orient="index")
    return [Hit(key, score, rows[key], rows[key]["description"]) for key, score in ranked]


def timed(call, repetitions: int = 5) -> dict:
    call()
    durations = []
    for _ in range(repetitions):
        start = time.perf_counter()
        call()
        durations.append((time.perf_counter() - start) * 1000)
    return {
        "repetitions": repetitions,
        "milliseconds": durations,
        "median_ms": float(np.median(durations)),
    }


def evidence(name: str, measurements: dict, *, tier: int = 1) -> Path:
    """Teaching diagnostics are kept separate from comparable harness leaderboards."""
    path = cache_dir() / f"tier{tier}" / "measurements" / f"{name}-{uuid.uuid4().hex[:8]}.json"
    atomic_json(
        path,
        {
            "name": name,
            "created_at": datetime.now(UTC).isoformat(),
            "seed": 20261104 if tier == 1 else measurements.get("seed", 42),
            "hardware": hardware(),
            "provenance": provenance(),
            "reference_artifacts": {
                name: file_hash(data_dir() / name)
                for name in [
                    "products_10k.parquet",
                    "embeddings_10k.parquet",
                    "query_embeddings.parquet",
                ]
            },
            "scope": "Teaching diagnostic; the named script states which artifacts or seeded math inputs it uses.",
            "measurements": measurements,
        },
    )
    print(f"Evidence: {path.relative_to(ROOT)}")
    return path
