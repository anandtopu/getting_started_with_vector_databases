"""Shared catalog inputs and independent exact comparisons for Tier 2 demonstrations."""

import numpy as np

from common.bench.ground_truth import neighbor_reference
from common.bench.metrics import tie_aware_recall
from common.data import records_from_products
from common.stores.registry import make_store
from common.stores.types import CollectionSpec
from common.teaching import catalog, timed


def trial(kind, limit=400, k=10, expression=None, **settings):
    products, vectors, query, meta = catalog(limit)
    records = records_from_products(products, vectors)
    ids = [r.id for r in records]
    reference = neighbor_reference(
        vectors, ids, [r.metadata for r in records], query, k, "cosine", expression
    )
    store = make_store("ann", kind=kind, **settings)
    try:
        store.create_collection(
            CollectionSpec("products", vectors.shape[1], "cosine", meta["space"])
        )
        store.upsert(records)
        store.build()

        def search():
            return store.search(query, k, expression)

        found = [h.id for h in search()]
        return {
            "kind": kind,
            "parameters": settings,
            "products": limit,
            "query": "q000",
            "ids": found,
            "recall": tie_aware_recall(found, reference, k),
            "index_payload_bytes": int(store.index.payload_bytes),
            "timings": timed(search),
        }
    finally:
        store.close()


def unit_catalog(count):
    products, matrix, query, _ = catalog(count)
    return (
        products,
        matrix / np.linalg.norm(matrix, axis=1, keepdims=True),
        query / np.linalg.norm(query),
    )


def prefix_results():
    import json

    from common.io import file_hash
    from common.settings import ROOT

    directory = ROOT / "data/tier2"
    manifest = json.loads((directory / "manifest.json").read_text())
    if file_hash(directory / "matryoshka.npz") != manifest["sha256"]["matryoshka.npz"]:
        raise ValueError("Invalid Qwen sample checksum")
    with np.load(directory / "matryoshka.npz", allow_pickle=False) as sample:
        matrix = sample["documents"]
        query = sample["query"]
        ids = sample["ids"]
    out = {}
    for d in [1024, 512, 256, 64, 32]:
        vectors = matrix[:, :d]
        scores = (vectors @ query[:d]) / (
            np.linalg.norm(vectors, axis=1) * np.linalg.norm(query[:d])
        )
        out[str(d)] = {
            "top10": ids[np.argsort(-scores, kind="stable")[:10]].tolist(),
            "vector_bytes": vectors.size * 4,
        }
    return out
