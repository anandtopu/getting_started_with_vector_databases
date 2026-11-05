"""Update a Chroma listing, reopen the local file and query its metadata.

Run: uv run --extra embedded python modules/11_embedded/examples/02_production.py
Concepts: Update a Chroma listing, reopen the local file and query its metadata.
Expected: Chroma reopened IDs and updated region.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
import uuid

import chromadb

from common.settings import cache_dir
from common.teaching import catalog


def main() -> None:
    # KEY IDEA: Update a Chroma listing, reopen the local file and query its metadata.
    path = str(cache_dir() / "tier3/chroma")
    products, matrix, q, _ = catalog(100)
    name = "native_" + uuid.uuid4().hex
    with chromadb.PersistentClient(
        path=path, settings=chromadb.Settings(anonymized_telemetry=False)
    ) as db:
        table = db.create_collection(
            name, embedding_function=None, configuration={"hnsw": {"space": "cosine"}}
        )
        table.upsert(
            ids=products.id.tolist(),
            embeddings=matrix.tolist(),
            documents=products.title.tolist(),
            metadatas=[{"region": r} for r in products.region],
        )
        key = products.id.iloc[0]
        table.update(ids=[key], metadatas=[{"region": "special"}])
    with chromadb.PersistentClient(
        path=path, settings=chromadb.Settings(anonymized_telemetry=False)
    ) as db:
        table = db.get_collection(name, embedding_function=None)
        try:
            hit = table.query(
                query_embeddings=[q.tolist()], where={"region": "special"}, n_results=1
            )
            print(hit["ids"], table.get(ids=[key])["documents"])
            assert hit["ids"] == [[key]]
            table.delete(ids=[key])
            assert table.count() == 99
        finally:
            db.delete_collection(name)


if __name__ == "__main__":
    main()
