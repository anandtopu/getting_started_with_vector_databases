"""An offline-capable search session shared by examples and the Playground."""

import time

from common.data import load_products, load_vectors, records_from_products, search_queries
from common.embeddings import TextEncoder, cached_texts, frozen_query
from common.settings import data_dir
from common.stores.registry import make_store
from common.stores.types import CollectionSpec


def open_catalog(backend: str = "tinyvec", limit: int = 10_000, **parameters):
    products = load_products(limit=limit)
    vectors, metadata = load_vectors(data_dir() / "embeddings_10k.parquet", products)
    store = make_store(backend, **parameters)
    store.create_collection(
        CollectionSpec("marlowe", vectors.shape[1], "cosine", metadata["space"])
    )
    store.upsert(records_from_products(products, vectors))
    if hasattr(store, "build"):
        store.build()
    return store, products, vectors


def search_saved(store, query_id: str = "q000", k: int = 5, expression: dict | None = None):
    query = next(q for q in search_queries() if q["id"] == query_id)
    vector, metadata = frozen_query(query_id, data_dir())
    start = time.perf_counter()
    hits = store.search(
        vector,
        k,
        expression if expression is not None else query["filter"],
        space=metadata["space"],
    )
    return query, hits, (time.perf_counter() - start) * 1000


def search_text(store, text: str, k: int = 5, expression: dict | None = None):
    encoder = TextEncoder()
    vector = cached_texts([text], encoder, "query")[0]
    start = time.perf_counter()
    hits = store.search(vector, k, expression, space=encoder.spec.space)
    return hits, (time.perf_counter() - start) * 1000
