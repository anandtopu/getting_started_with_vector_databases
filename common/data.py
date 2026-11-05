"""Load aligned products/vectors and reject stale or mismatched artifacts."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from common.errors import CourseError
from common.io import file_hash, read_jsonl
from common.settings import data_dir
from common.stores.types import Record


def load_products(path: Path | None = None, limit: int | None = None) -> pd.DataFrame:
    path = path or data_dir() / "products_10k.parquet"
    if not path.exists():
        raise CourseError("Catalog missing. Run: uv run python scripts/build_data.py")
    if limit is None:
        return pd.read_parquet(path)
    if limit < 1:
        raise ValueError("limit must be positive")
    batches = []
    remaining = limit
    for batch in pq.ParquetFile(path).iter_batches(batch_size=min(limit, 4096)):
        batches.append(batch.slice(0, remaining).to_pandas())
        remaining -= len(batches[-1])
        if remaining <= 0:
            break
    return pd.concat(batches, ignore_index=True)


def load_vectors(path: Path, products: pd.DataFrame | None = None) -> tuple[np.ndarray, dict]:
    manifest_path = path.with_suffix(".manifest.json")
    if not path.exists() or not manifest_path.exists():
        raise CourseError(
            f"Embedding artifact missing: {path}. Run scripts/embed_data.py with --download once."
        )
    metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
    if file_hash(path) != metadata["sha256"]:
        raise CourseError(f"Embedding checksum failed: {path}")
    table = pq.read_table(path)
    vectors = np.asarray(table["vector"].to_pylist(), dtype=np.float32)
    if products is not None:
        ids = table["id"].to_pylist()
        lookup = {key: i for i, key in enumerate(ids)}
        try:
            positions = [lookup[key] for key in products["id"]]
        except KeyError as exc:
            raise CourseError(f"No embedding for product {exc.args[0]}") from exc
        vectors = vectors[positions]
        if "content_hash" in table.column_names:
            from common.io import digest

            hashes = table["content_hash"].to_pylist()
            for position, text in zip(positions, product_texts(products), strict=True):
                if hashes[position] != digest(text):
                    raise CourseError("Catalog text changed after embedding; rebuild the vectors.")
    if vectors.ndim != 2 or not np.isfinite(vectors).all():
        raise CourseError("Invalid embedding matrix")
    return vectors, metadata


def product_texts(products: pd.DataFrame) -> list[str]:
    return (products["title"] + ". " + products["description"]).tolist()


def records_from_products(products: pd.DataFrame, vectors: np.ndarray) -> list[Record]:
    if len(products) != len(vectors):
        raise ValueError("Product and embedding counts differ")
    rows = products.to_dict(orient="records")
    result = []
    for row, vector in zip(rows, vectors, strict=True):
        tags = row.get("tags", [])
        metadata = {
            key: row[key]
            for key in ("category", "kind", "price", "stock", "seller_id", "region", "sku", "color")
        }
        metadata["tags"] = list(tags)
        metadata["title"] = row["title"]
        result.append(Record(row["id"], vector, metadata, row["title"] + ". " + row["description"]))
    return result


def search_queries(directory: Path | None = None) -> list[dict]:
    return read_jsonl((directory or data_dir()) / "eval/search_qrels.jsonl")
