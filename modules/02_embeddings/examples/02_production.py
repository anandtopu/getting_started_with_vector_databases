"""Reuse cached real vectors in an embedded search engine.

Concepts: cache key, model identity, explicit vectors, model-free retrieval.
Run: uv run --extra embedded python modules/02_embeddings/examples/02_production.py
Expected: repeated cached arrays agree; Chroma returns mug warmers
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

# course-extra: embedded
import tempfile
import time
import uuid
from pathlib import Path

import chromadb
import numpy as np

from common.data import product_texts
from common.embeddings import EmbeddingCache, EmbeddingSpec
from common.pretty import show_hits
from common.teaching import catalog, ranked_hits


def main() -> None:
    products, vectors, query, metadata = catalog(200)
    texts = product_texts(products)
    # These are real precomputed vectors; the provider is a lookup, not model inference.
    lookup = dict(zip(texts, vectors, strict=True))
    calls = []

    def provider(missing, role):
        calls.append(len(missing))
        return np.stack([lookup[text] for text in missing])

    with tempfile.TemporaryDirectory() as directory:
        cache = EmbeddingCache(Path(directory))
        spec = EmbeddingSpec(**metadata["model"])
        first = cache.encode(texts, spec, "document", provider)
        second = cache.encode(texts, spec, "document", provider)
        np.testing.assert_array_equal(first, second)
        assert len(calls) == 1
    client = chromadb.EphemeralClient(settings=chromadb.Settings(anonymized_telemetry=False))
    name = "cached_" + uuid.uuid4().hex
    collection = client.create_collection(
        name, embedding_function=None, configuration={"hnsw": {"space": "cosine"}}
    )
    try:
        collection.add(ids=products["id"].tolist(), embeddings=second.tolist())
        start = time.perf_counter()
        found = collection.query(query_embeddings=[query.tolist()], n_results=5)
        elapsed = (time.perf_counter() - start) * 1000
        ranked = list(zip(found["ids"][0], [1 - d for d in found["distances"][0]], strict=True))
        show_hits(ranked_hits(products, ranked), elapsed, title="Reuse embeddings")
        print("Provider calls:", len(calls))
    finally:
        client.delete_collection(name)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
