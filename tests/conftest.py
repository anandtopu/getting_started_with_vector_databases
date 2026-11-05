"""Tests never download models or contact services unless explicitly selected."""

import os

import numpy as np
import pytest

from common.stores.registry import make_store
from common.stores.types import CollectionSpec, Record

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["ANONYMIZED_TELEMETRY"] = "False"


@pytest.fixture(
    params=["tinyvec", pytest.param("sqlite-vec", marks=pytest.mark.embedded), "faiss-flat"]
)
def store(request, tmp_path):
    if request.param == "faiss-flat":
        pytest.importorskip("faiss", reason="Install --extra libs for FAISS contracts")
    if request.param == "sqlite-vec":
        pytest.importorskip(
            "sqlite_vec", reason="Install --extra embedded to run SQLite adapter contracts"
        )
    instance = make_store(request.param, path=tmp_path / "test.db")
    instance.create_collection(CollectionSpec("test", 3, "cosine", "fixture-v1"))
    yield instance
    instance.close()


@pytest.fixture
def rows():
    return [
        Record(
            "a",
            np.array([1, 0, 0], dtype=np.float32),
            {"tenant": "one", "price": 10, "stock": 1, "active": True},
            "red mug",
        ),
        Record(
            "b",
            np.array([0.8, 0.2, 0], dtype=np.float32),
            {"tenant": "two", "price": 12, "stock": 0},
            "blue mug",
        ),
        Record(
            "c",
            np.array([0, 1, 0], dtype=np.float32),
            {"tenant": "one", "price": 9.0, "stock": 3},
            "chair",
        ),
        Record("d", np.array([1, 0, 0], dtype=np.float32), {"tenant": "one"}, "duplicate mug"),
    ]
