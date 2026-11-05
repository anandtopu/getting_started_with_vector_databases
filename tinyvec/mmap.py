"""Stream fixed-width synthetic vectors to a scalar-quantized, memory-mapped scan."""

import time
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits

from common.bench.resources import MemorySampler


def merge_best(old, values, start, k):
    # Keep stable boundary ties within each block and across blocks.
    ids = np.arange(start, start + len(values))
    local = np.lexsort((ids, -values))[:k]
    return sorted(
        old + [(float(values[i]), int(ids[i])) for i in local], key=lambda row: (-row[0], row[1])
    )[:k]


def experiment(directory: Path, rows=1_000_000, dimensions=32, block=8192, seed=42):
    if min(rows, dimensions, block) < 1:
        raise ValueError("Rows, dimensions and block size must be positive")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "codes.npy"
    queries = np.random.default_rng(seed + 1).standard_normal((5, dimensions), dtype=np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)
    truth = [[] for _ in queries]
    rng = np.random.default_rng(seed)
    with threadpool_limits(limits=1), MemorySampler() as memory:
        start = time.perf_counter()
        codes = np.lib.format.open_memmap(path, mode="w+", dtype="int8", shape=(rows, dimensions))
        for offset in range(0, rows, block):
            vectors = rng.standard_normal((min(block, rows - offset), dimensions), dtype=np.float32)
            vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
            codes[offset : offset + len(vectors)] = np.rint(127 * vectors).astype("int8")
            for i, scores in enumerate((vectors @ queries.T).T):
                truth[i] = merge_best(truth[i], scores, offset, 10)
        codes.flush()
        del codes
        build = time.perf_counter() - start
        mapped = np.load(path, mmap_mode="r")
        timings = []
        recalls = []
        for q, expected in zip(queries, truth, strict=True):
            start = time.perf_counter()
            ranked = []
            for offset in range(0, rows, block):
                values = mapped[offset : offset + block] @ q
                ranked = merge_best(ranked, values, offset, 10)
            timings.append(time.perf_counter() - start)
            recalls.append(len({r for _, r in expected} & {r for _, r in ranked}) / len(expected))
        del mapped
    return {
        "rows": rows,
        "dimensions": dimensions,
        "seed": seed,
        "block": block,
        "queries": len(queries),
        "dtype": "int8",
        "file_bytes": path.stat().st_size,
        "build_and_float_truth_seconds": build,
        "query_seconds": timings,
        "recall_at_10": recalls,
        "memory": memory.report(),
        "bytes_per_scan": rows * dimensions,
        "page_cache": "OS managed; no cold-cache eviction attempted",
    }
