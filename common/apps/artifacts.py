"""Small real-model artifacts with model, content and file checksums."""

import json
from dataclasses import asdict

import numpy as np

from common.errors import CourseError
from common.io import atomic_json, digest, file_hash
from common.settings import data_dir


def save_artifact(name, ids, contents, vectors, spec, role):
    directory = data_dir() / "tier4"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.npz"
    if len(ids) != len(vectors) or len(ids) != len(contents) or len(set(ids)) != len(ids):
        raise ValueError("Artifact rows must have unique aligned IDs")
    np.savez_compressed(path, ids=np.asarray(ids), vectors=np.asarray(vectors, dtype=np.float32))
    atomic_json(
        path.with_suffix(".json"),
        {
            "format": 1,
            "model": asdict(spec),
            "space": spec.space,
            "role": role,
            "rows": len(ids),
            "content_hash": digest(contents),
            "sha256": file_hash(path),
        },
    )


def load_artifact(name, *, contents=None):
    path = data_dir() / "tier4" / f"{name}.npz"
    if not path.exists():
        raise CourseError(
            f"Prepare real application vectors: uv run --extra models python scripts/prepare_tier4.py --{name.split('_')[0]} --download"
        )
    meta = json.loads(path.with_suffix(".json").read_text(encoding="utf8"))
    if file_hash(path) != meta["sha256"] or (
        contents is not None and digest(contents) != meta["content_hash"]
    ):
        raise CourseError(f"Stale or corrupt Tier 4 artifact: {name}. Rebuild it.")
    with np.load(path, allow_pickle=False) as arrays:
        ids, vectors = arrays["ids"].tolist(), arrays["vectors"].copy()
    if (
        vectors.shape != (len(ids), meta["model"]["dimensions"])
        or not np.isfinite(vectors).all()
        or len(set(ids)) != len(ids)
    ):
        raise CourseError(f"Invalid Tier 4 matrix: {name}")
    return ids, vectors, meta
