"""Load genuine frozen application artifacts without downloading a model."""

import pandas as pd

from common.apps.artifacts import load_artifact
from common.apps.multimodal import MultimodalSearch
from common.apps.rag import RagAssistant, load_chunks
from common.data import load_products, product_texts
from common.io import file_hash, read_jsonl
from common.settings import data_dir


def open_rag(database):
    chunks = load_chunks(data_dir() / "help_center")
    ids, vectors, meta = load_artifact("rag_chunks", contents=[c.text for c in chunks])
    if ids != [c.id for c in chunks]:
        raise ValueError("Chunk IDs changed. Rebuild Tier 4 artifacts.")
    qa = read_jsonl(data_dir() / "eval/rag_qa.jsonl")
    qids, queries, qm = load_artifact("rag_queries", contents=[q["question"] for q in qa])
    if qm["space"] != meta["space"]:
        raise ValueError("RAG query and passage spaces differ")
    return (
        RagAssistant(database, chunks, vectors, meta["space"]),
        qa,
        dict(zip(qids, queries, strict=True)),
    )


def open_photos(database, seller_id=None, excluded_ids=()):
    ids, images, meta = load_artifact("image_gallery")
    products = load_products(limit=len(ids))
    paths = [data_dir() / "tier4/images" / f"{key}.png" for key in ids]
    load_artifact("image_gallery", contents=[file_hash(path) for path in paths])
    tids, texts, tm = load_artifact("image_titles", contents=product_texts(products))
    if tids != ids or tm["space"] != meta["space"]:
        raise ValueError("Image and text spaces must match")
    if seller_id is not None or excluded_ids:
        mask = ~products.id.isin(excluded_ids)
        if seller_id is not None:
            mask &= products.seller_id == seller_id
        products = products.loc[mask].reset_index(drop=True)
        ids = products.id.tolist()
        images, texts = images[mask.to_numpy()], texts[mask.to_numpy()]
    metadata = {
        r["id"]: {k: r[k] for k in ["title", "kind", "color", "price", "region", "seller_id"]}
        for r in products.to_dict("records")
    }
    model = MultimodalSearch(database, ids, images, texts, meta["space"], metadata)
    return model, images, texts


def review_data():
    ids, vectors, meta = load_artifact("reviews")
    rows = pd.read_parquet(data_dir() / "tier4/reviews.parquet").head(len(ids))
    load_artifact("reviews", contents=rows.text.tolist())
    if ids != rows.id.tolist():
        raise ValueError("Review IDs changed")
    return rows, vectors, meta
