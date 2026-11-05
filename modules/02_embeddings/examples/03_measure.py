"""Measure batching and cache behavior without hidden downloads.

Concepts: cold/warm cache, role and prefix identity, optional real CPU inference.
Run: uv run python modules/02_embeddings/examples/03_measure.py
Expected: matching arrays, distinct role/prefix keys, measured cache timings
CPU: about 2–10; --live about 30–60 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import argparse
import tempfile
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from common.bench.resources import MemorySampler
from common.embeddings import EmbeddingCache, HashEncoder, TextEncoder
from common.teaching import catalog, evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live", action="store_true", help="Use cached MiniLM; requires --extra models"
    )
    args = parser.parse_args()
    with MemorySampler() as memory:
        measurements = experiment(args.live)
    measurements["memory"] = memory.report()
    evidence("embedding_cache_live" if args.live else "embedding_cache", measurements)


def experiment(live: bool) -> dict:
    texts = catalog(64)[0]["description"].tolist()
    encoder = TextEncoder(batch_size=16) if live else HashEncoder()
    start = time.perf_counter()
    encoder.encode(texts[:1])
    startup = time.perf_counter() - start
    batches = {}
    for size in [1, 16, 32]:
        if live:
            encoder.batch_size = size
        repeats = []
        for _ in range(5):
            start = time.perf_counter()
            values = np.concatenate(
                [encoder.encode(texts[i : i + size]) for i in range(0, len(texts), size)]
            )
            repeats.append(time.perf_counter() - start)
        batches[str(size)] = repeats
        assert values.shape == (64, encoder.spec.dimensions)
    with tempfile.TemporaryDirectory() as directory:
        cache = EmbeddingCache(Path(directory))
        timings = []
        for _ in range(6):
            start = time.perf_counter()
            cached = cache.encode(texts, encoder.spec, "document", encoder.encode)
            timings.append(time.perf_counter() - start)
        np.testing.assert_allclose(values, cached, atol=2e-6)
        # KEY IDEA: adding a prefix changes the space even if dimension count stays identical.
        changed = replace(encoder.spec, query_prefix="query: ")
        assert cache.key(texts[0], changed, "query") != cache.key(texts[0], encoder.spec, "query")
        assert cache.key(texts[0], encoder.spec, "document") != cache.key(
            texts[0], encoder.spec, "query"
        )
    label = "real cached MiniLM" if live else "hash mechanics only; no semantic-quality claim"
    print(label, "batch seconds:", batches, "miss/hit seconds:", timings)
    return {
        "encoder": label,
        "startup_seconds": startup,
        "batch_seconds": batches,
        "cache_miss_hit_seconds": timings,
        "space": encoder.spec.space,
    }


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
