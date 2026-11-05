"""Compute genuine MiniLM vectors and cache them by content and immutable model revision.

Run: uv run --extra models python scripts/embed_data.py --download
Expected: Wrote 10,000 product vectors and 300 query vectors. CPU: several minutes.
Needs: generated catalog, models extra, 91 MB model download on first explicit preparation.
No Docker. After preparation, omit --download to require cached model files.
"""

import argparse
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from common.data import load_products, product_texts, search_queries
from common.embeddings import TextEncoder, cached_texts
from common.errors import run_cli
from common.io import atomic_json, digest, file_hash
from common.settings import data_dir


def write_vectors(
    path: Path,
    ids: list[str],
    texts: list[str],
    vectors: np.ndarray,
    encoder: TextEncoder,
    role: str,
) -> None:
    array = pa.FixedSizeListArray.from_arrays(
        pa.array(vectors.astype(np.float16).ravel(), type=pa.float16()), encoder.spec.dimensions
    )
    table = pa.table({"id": ids, "vector": array, "content_hash": [digest(text) for text in texts]})
    pq.write_table(table, path, compression="zstd")
    atomic_json(
        path.with_suffix(".manifest.json"),
        {
            "format": 1,
            "rows": len(ids),
            "model": asdict(encoder.spec),
            "space": encoder.spec.space,
            "role": role,
            "storage_dtype": "float16",
            "sha256": file_hash(path),
            "created_at": datetime.now(UTC).isoformat(),
            "license": "Derived from synthetic MIT data using Apache-2.0 model; see data/README.md",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--download", action="store_true", help="Allow the explicitly requested model download"
    )
    parser.add_argument(
        "--full", action="store_true", help="Embed full products.parquet in bounded batches"
    )
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    encoder = TextEncoder(download=args.download, batch_size=args.batch_size)
    directory = data_dir()
    if args.full:
        source = directory / "products.parquet"
        destination = directory / "embeddings_full.parquet"
        total = 0
        writer = None
        try:
            for batch in pq.ParquetFile(source).iter_batches(batch_size=1024):
                products = batch.to_pandas()
                texts = product_texts(products)
                vectors = cached_texts(texts, encoder)
                array = pa.FixedSizeListArray.from_arrays(
                    pa.array(vectors.astype(np.float16).ravel(), type=pa.float16()),
                    encoder.spec.dimensions,
                )
                table = pa.table(
                    {
                        "id": products["id"].tolist(),
                        "vector": array,
                        "content_hash": [digest(text) for text in texts],
                    }
                )
                if writer is None:
                    writer = pq.ParquetWriter(destination, table.schema, compression="zstd")
                writer.write_table(table)
                total += len(products)
        finally:
            if writer is not None:
                writer.close()
        atomic_json(
            destination.with_suffix(".manifest.json"),
            {
                "format": 1,
                "rows": total,
                "model": asdict(encoder.spec),
                "space": encoder.spec.space,
                "role": "document",
                "storage_dtype": "float16",
                "sha256": file_hash(destination),
                "created_at": datetime.now(UTC).isoformat(),
            },
        )
        print(f"Wrote {total:,} full-catalog vectors.")
    else:
        products = load_products()
        texts = product_texts(products)
        vectors = cached_texts(texts, encoder)
        write_vectors(
            directory / "embeddings_10k.parquet",
            products["id"].tolist(),
            texts,
            vectors,
            encoder,
            "document",
        )
        print(f"Wrote {len(products):,} product vectors.")
    queries = search_queries()
    texts = [q["text"] for q in queries]
    vectors = cached_texts(texts, encoder, "query")
    write_vectors(
        directory / "query_embeddings.parquet",
        [q["id"] for q in queries],
        texts,
        vectors,
        encoder,
        "query",
    )
    print(
        f"Wrote {len(queries):,} query vectors. Photo queries here are text surrogates; image evaluation belongs to Tier 4."
    )


if __name__ == "__main__":
    run_cli(main)
