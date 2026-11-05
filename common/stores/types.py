"""Portable records and explicit metric/embedding-space contracts."""

import copy
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from common.io import canonical_json

Vector = NDArray[np.float32]
Metric = Literal["cosine", "dot", "l2"]


@dataclass(frozen=True)
class CollectionSpec:
    name: str
    dimensions: int
    metric: Metric = "cosine"
    space: str = "hash-v1"

    def __post_init__(self) -> None:
        if not self.name or self.dimensions <= 0 or self.metric not in {"cosine", "dot", "l2"}:
            raise ValueError(
                "Collection needs a name, positive dimensions, and cosine/dot/l2 metric."
            )
        if not self.space:
            raise ValueError("Embedding space must identify the model and preprocessing.")


@dataclass(frozen=True)
class Record:
    id: str
    vector: Vector
    metadata: dict = field(default_factory=dict)
    text: str = ""

    def copy(self) -> "Record":
        return Record(self.id, self.vector.copy(), copy.deepcopy(self.metadata), self.text)


@dataclass(frozen=True)
class Hit:
    id: str
    score: float
    metadata: dict
    text: str = ""
    native_score: float | None = None


@dataclass(frozen=True)
class Capabilities:
    persistence: bool = True
    hybrid: Literal["none", "native", "application"] = "none"
    named_vectors: bool = False
    approximate: bool = False


def checked_vector(vector: object, spec: CollectionSpec) -> Vector:
    array = np.array(vector, dtype=np.float32, copy=True)
    if array.shape != (spec.dimensions,) or not np.isfinite(array).all():
        raise ValueError(
            f"Expected {spec.dimensions} finite vector values; got shape {array.shape}."
        )
    if spec.metric == "cosine" and np.linalg.norm(array) == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector.")
    return array


def checked_record(record: Record, spec: CollectionSpec) -> Record:
    if not isinstance(record.id, str) or not record.id:
        raise ValueError("Record IDs must be non-empty strings.")
    if not isinstance(record.metadata, dict) or not isinstance(record.text, str):
        raise ValueError("Record metadata must be a JSON object and text must be a string.")
    canonical_json(record.metadata)
    return Record(
        record.id, checked_vector(record.vector, spec), copy.deepcopy(record.metadata), record.text
    )
