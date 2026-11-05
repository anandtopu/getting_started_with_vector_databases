"""Use Chroma IDs, metadata, persistence, and CRUD.

Concepts: persistent collection, explicit embeddings, replace/delete/filter.
Run: uv run --extra embedded python modules/03_tinyvec/examples/02_production.py
Expected: one north-region item after update and delete; reopen count 1
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

# course-extra: embedded
import uuid

import chromadb

from common.settings import cache_dir


def main() -> None:
    path = cache_dir() / "tier1" / ("chroma-" + uuid.uuid4().hex)
    client = chromadb.PersistentClient(
        path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    collection = client.create_collection(
        "desk", embedding_function=None, configuration={"hnsw": {"space": "cosine"}}
    )
    collection.upsert(
        ids=["warmer", "flask"],
        embeddings=[[1.0, 0.1], [0.8, 1.0]],
        metadatas=[{"region": "north", "price": 30}, {"region": "south", "price": 25}],
    )
    collection.upsert(
        ids=["warmer"], embeddings=[[1.0, 0.1]], metadatas=[{"region": "north", "price": 20}]
    )
    found = collection.query(query_embeddings=[[1.0, 0.0]], n_results=2, where={"region": "north"})
    assert found["ids"] == [["warmer"]]
    collection.delete(ids=["flask"])
    # KEY IDEA: metadata and IDs live in the engine; the model still belongs to the application.
    reopened = chromadb.PersistentClient(
        path=str(path), settings=chromadb.Settings(anonymized_telemetry=False)
    )
    assert reopened.get_collection("desk", embedding_function=None).count() == 1
    print("Reopened count: 1; persistent files:", path)
    print("This is same-process reopen; a fresh-process restore check is part of the checkpoint.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
