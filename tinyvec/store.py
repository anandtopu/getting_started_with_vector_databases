"""Exact in-memory vector search with atomic, checksummed snapshots.

Mutations validate the entire batch before changing state. Search uses bounded
blocks and prefilters eligible records. Ties are resolved by string ID.
"""

import copy
import json
import os
import uuid
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path

import numpy as np

from common.errors import CourseError
from common.io import atomic_json, file_hash
from common.stores.filters import Filter, matches, parse_filter
from common.stores.types import (
    Capabilities,
    CollectionSpec,
    Hit,
    Record,
    checked_record,
    checked_vector,
)
from tinyvec.metrics import scores


class TinyVec:
    capabilities = Capabilities()

    def __init__(self, block_size: int = 4096) -> None:
        if block_size < 1:
            raise ValueError("block_size must be positive")
        self.block_size = block_size
        self.spec: CollectionSpec | None = None
        self._records: dict[str, Record] = {}
        self._matrix: np.ndarray | None = None
        self._ids: list[str] = []

    def create_collection(self, spec: CollectionSpec) -> None:
        if self.spec is not None and self.spec != spec:
            raise ValueError("Collection already exists with a different schema.")
        self.spec = spec

    def _require_spec(self) -> CollectionSpec:
        if self.spec is None:
            raise ValueError("Create a collection before using the store.")
        return self.spec

    def insert(self, records: Iterable[Record]) -> None:
        """Insert new IDs only; reject the whole batch if an ID already exists."""
        spec = self._require_spec()
        checked = [checked_record(record, spec) for record in records]
        ids = [record.id for record in checked]
        if len(set(ids)) != len(ids) or any(key in self._records for key in ids):
            raise ValueError("Insert requires new unique IDs; use upsert for replacement.")
        self._records.update((record.id, record) for record in checked)
        self._matrix = None

    def upsert(self, records: Iterable[Record]) -> None:
        checked = [checked_record(record, self._require_spec()) for record in records]
        for record in checked:
            self._records[record.id] = record
        self._matrix = None

    def delete(self, ids: Iterable[str]) -> None:
        self._require_spec()
        for record_id in ids:
            self._records.pop(record_id, None)
        self._matrix = None

    def records(self) -> list[Record]:
        return [self._records[key].copy() for key in sorted(self._records)]

    def build(self) -> None:
        spec = self._require_spec()
        self._ids = sorted(self._records)
        self._matrix = (
            np.stack([self._records[key].vector for key in self._ids])
            if self._ids
            else np.empty((0, spec.dimensions), dtype=np.float32)
        )

    def search(
        self,
        vector: object,
        k: int = 10,
        filter: Filter | dict | None = None,
        *,
        space: str | None = None,
    ) -> list[Hit]:
        spec = self._require_spec()
        if isinstance(k, bool) or not isinstance(k, int) or k < 1:
            raise ValueError("k must be a positive integer")
        if space is not None and space != spec.space:
            raise ValueError("Query embedding space does not match this collection.")
        query = checked_vector(vector, spec)
        expression = parse_filter(filter)
        if self._matrix is None:
            self.build()
        eligible = [
            i for i, key in enumerate(self._ids) if matches(self._records[key].metadata, expression)
        ]
        best: list[tuple[float, str]] = []
        for start in range(0, len(eligible), self.block_size):
            positions = eligible[start : start + self.block_size]
            values = scores(self._matrix[positions], query, spec.metric)
            # KEY IDEA: retaining only k winners from each block preserves exact top-k.
            block = sorted(
                zip(values.tolist(), (self._ids[i] for i in positions), strict=True),
                key=lambda item: (-item[0], item[1]),
            )[:k]
            best = sorted(best + block, key=lambda item: (-item[0], item[1]))[:k]
        return [
            Hit(
                key,
                float(score),
                copy.deepcopy(self._records[key].metadata),
                self._records[key].text,
                float(score),
            )
            for score, key in best
        ]

    def hybrid_search(self, *args: object, **kwargs: object) -> list[Hit]:
        raise CourseError("For hybrid search use the Tier 2 indexed TinyVec backend (ann).")

    def save(self, path: Path) -> None:
        spec = self._require_spec()
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        generation = uuid.uuid4().hex
        records = self.records()
        vector_path = path / f"vectors-{generation}.npy"
        matrix = (
            np.stack([r.vector for r in records])
            if records
            else np.empty((0, spec.dimensions), dtype=np.float32)
        )
        with vector_path.open("wb") as stream:
            np.save(stream, matrix, allow_pickle=False)
            stream.flush()
            os.fsync(stream.fileno())
        # Publish the pointer last: interrupted saves leave the previous snapshot readable.
        atomic_json(
            path / "snapshot.json",
            {
                "format": 1,
                "options": self.snapshot_options(),
                "spec": asdict(spec),
                "vectors": vector_path.name,
                "sha256": file_hash(vector_path),
                "records": [{"id": r.id, "metadata": r.metadata, "text": r.text} for r in records],
            },
        )

    @classmethod
    def load(cls, path: Path) -> "TinyVec":
        path = Path(path).resolve()
        manifest = json.loads((path / "snapshot.json").read_text(encoding="utf-8"))
        if manifest["format"] != 1:
            raise ValueError("Unsupported TinyVec snapshot format")
        vector_path = (path / manifest["vectors"]).resolve()
        if vector_path.parent != path or file_hash(vector_path) != manifest["sha256"]:
            raise ValueError("Invalid snapshot path or checksum")
        matrix = np.load(vector_path, allow_pickle=False)
        if len(matrix) != len(manifest["records"]):
            raise ValueError("Snapshot row count mismatch")
        store = cls(**manifest.get("options", {}))
        store.create_collection(CollectionSpec(**manifest["spec"]))
        store.upsert(
            Record(vector=vector, **row)
            for row, vector in zip(manifest["records"], matrix, strict=True)
        )
        return store

    def close(self) -> None:
        self._matrix = None

    def snapshot_options(self) -> dict:
        return {}
