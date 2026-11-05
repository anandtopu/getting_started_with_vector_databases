"""Prepare a checksummed Fashion-MNIST ANN subset from a pinned official source.

Run: uv run python scripts/download_benchmarks.py --download
Expected: 10,000 base and 1,000 query vectors in data/benchmarks/fashion-mnist/subset.npz.
Needs: ~31 MB download, ~100 MB RAM, ~80 MB disk. MIT license is saved beside data.
No download occurs without --download; cached files are always checksum verified.
"""

import argparse
import gzip
import json
import struct
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

from common.errors import CourseError, run_cli
from common.io import atomic_json, file_hash
from common.settings import ROOT, data_dir


def ensure_file(path: Path, url: str, expected: str, download: bool) -> None:
    if not path.exists():
        if not download:
            raise CourseError(
                f"Missing {path.name}. Rerun with --download to fetch the licensed dataset."
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(path.suffix + ".partial")
        try:
            with urllib.request.urlopen(url, timeout=30) as response, partial.open("wb") as stream:
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    stream.write(block)
            if file_hash(partial) != expected:
                raise CourseError(f"Checksum mismatch for {url}; refusing to use downloaded bytes.")
            partial.replace(path)
        except (OSError, urllib.error.URLError) as exc:
            raise CourseError(f"Download failed for {url}: {exc}. Retry the same command.") from exc
        finally:
            partial.unlink(missing_ok=True)
    if file_hash(path) != expected:
        raise CourseError(
            f"Cached benchmark checksum failed: {path}. Remove this file and download again."
        )


def read_idx(path: Path, count: int, seed: int) -> np.ndarray:
    with gzip.open(path, "rb") as stream:
        magic, rows, height, width = struct.unpack(">IIII", stream.read(16))
        if magic != 2051 or (height, width) != (28, 28) or not 1 <= count <= rows:
            raise CourseError("Unexpected IDX header or invalid requested subset size")
        values = np.frombuffer(stream.read(), dtype=np.uint8)
    if values.size != rows * height * width:
        raise CourseError("Truncated IDX benchmark data")
    selected = np.sort(np.random.default_rng(seed).choice(rows, count, replace=False))
    return values.reshape(rows, height * width)[selected].astype(np.float32) / 255.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--base", type=int, default=10_000)
    parser.add_argument("--queries", type=int, default=1000)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "docs/benchmark_datasets.json").read_text(encoding="utf-8"))
    destination = data_dir() / "benchmarks" / manifest["name"]
    for entry in manifest["files"]:
        ensure_file(destination / entry["name"], entry["url"], entry["sha256"], args.download)
    ensure_file(
        destination / "LICENSE", manifest["license_url"], manifest["license_sha256"], args.download
    )
    base = read_idx(destination / "train-images-idx3-ubyte.gz", args.base, 20261104)
    queries = read_idx(destination / "t10k-images-idx3-ubyte.gz", args.queries, 20261105)
    np.savez_compressed(destination / "subset.npz", base=base, queries=queries)
    atomic_json(
        destination / "subset.manifest.json",
        {
            "source": manifest,
            "base": args.base,
            "queries": args.queries,
            "dimensions": 784,
            "dtype": "float32",
            "metric": "l2",
            "seeds": [20261104, 20261105],
            "sha256": file_hash(destination / "subset.npz"),
            "note": "A laptop subset, not a reproduction of full-size published performance.",
        },
    )
    print(f"Prepared {args.base:,} base and {args.queries:,} query vectors in {destination}.")


if __name__ == "__main__":
    run_cli(main)
