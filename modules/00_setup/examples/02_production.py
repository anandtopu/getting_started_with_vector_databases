"""Give Chroma explicit precomputed vectors.

Concepts: embedded database, IDs, embedding function boundary.
Run: uv run --extra embedded python modules/00_setup/examples/02_production.py
Expected: five ceramic mug-warmer results
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

# course-extra: embedded
import time
import uuid

import chromadb

from common.pretty import show_hits
from common.teaching import catalog, ranked_hits


def main() -> None:
    products, vectors, query, _ = catalog()
    client = chromadb.EphemeralClient(settings=chromadb.Settings(anonymized_telemetry=False))
    name = "marlowe_" + uuid.uuid4().hex
    collection = client.create_collection(
        name, embedding_function=None, configuration={"hnsw": {"space": "cosine"}}
    )
    try:
        # KEY IDEA: the same vectors enter both engines; Chroma does not choose a model for us.
        collection.add(ids=products["id"].tolist(), embeddings=vectors.tolist())
        start = time.perf_counter()
        result = collection.query(query_embeddings=[query.tolist()], n_results=5)
        elapsed = (time.perf_counter() - start) * 1000
        ranked = list(zip(result["ids"][0], [1 - d for d in result["distances"][0]], strict=True))
        show_hits(ranked_hits(products, ranked), elapsed, title="Chroma explicit-vector search")
    finally:
        client.delete_collection(name)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
