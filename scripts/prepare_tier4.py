"""Prepare genuine application vectors, with an explicit one-time download switch.
Run: uv run --extra models python scripts/prepare_tier4.py --all --download
CPU: several minutes per model. Models load in separate processes with --all.
"""

import argparse
import subprocess
import sys

import pandas as pd

from common.apps.artifacts import save_artifact
from common.apps.rag import load_chunks
from common.data import load_products, product_texts, search_queries
from common.embeddings import (
    ImageTextEncoder,
    Reranker,
    TextEncoder,
    cached_texts,
    multilingual_spec,
)
from common.errors import run_cli
from common.io import file_hash, read_jsonl
from common.search.query_parser import parse_query
from common.settings import data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in [
        "all",
        "rag",
        "reviews",
        "queries",
        "multilingual",
        "image",
        "reranker",
        "download",
    ]:
        parser.add_argument("--" + name, action="store_true")
    args = parser.parse_args()
    if args.all:
        for name in ["rag", "reviews", "queries", "multilingual", "image", "reranker"]:
            subprocess.run(
                [sys.executable, __file__, "--" + name, *(["--download"] if args.download else [])],
                check=True,
            )
        return
    directory = data_dir()
    encoder = TextEncoder(download=args.download)
    if args.rag:
        chunks = load_chunks(directory / "help_center")
        texts = [c.text for c in chunks]
        save_artifact(
            "rag_chunks",
            [c.id for c in chunks],
            texts,
            cached_texts(texts, encoder),
            encoder.spec,
            "document",
        )
        qa = read_jsonl(directory / "eval/rag_qa.jsonl")
        texts = [q["question"] for q in qa]
        save_artifact(
            "rag_queries",
            [q["id"] for q in qa],
            texts,
            cached_texts(texts, encoder, "query"),
            encoder.spec,
            "query",
        )
        print(f"Prepared {len(chunks)} chunks and {len(qa)} questions", flush=True)
    if args.reviews:
        source = directory / "reviews.parquet"
        rows = pd.read_parquet(
            source if source.exists() else directory / "tier4/reviews.parquet"
        ).head(400)
        texts = rows.text.tolist()
        save_artifact(
            "reviews",
            rows.id.tolist(),
            texts,
            cached_texts(texts, encoder),
            encoder.spec,
            "document",
        )
        print("Prepared 400 real review vectors", flush=True)
    if args.queries:
        queries = [q for q in search_queries() if q["type"] != "photo"]
        texts = [parse_query(q["text"]).text or q["text"] for q in queries]
        save_artifact(
            "queries_parsed",
            [q["id"] for q in queries],
            texts,
            cached_texts(texts, encoder, "query"),
            encoder.spec,
            "query",
        )
        print("Prepared parsed queries", flush=True)
    if args.multilingual:
        encoder = TextEncoder(multilingual_spec(), download=args.download, batch_size=8)
        products = load_products(limit=500)
        texts = product_texts(products)
        save_artifact(
            "multilingual_products",
            products.id.tolist(),
            texts,
            cached_texts(texts, encoder),
            encoder.spec,
            "document",
        )
        queries = [q for q in search_queries() if q["type"] == "multilingual"]
        texts = [q["text"] for q in queries]
        save_artifact(
            "multilingual_queries",
            [q["id"] for q in queries],
            texts,
            cached_texts(texts, encoder, "query"),
            encoder.spec,
            "query",
        )
        print("Prepared Qwen: 500 products and 50 multilingual queries", flush=True)
    if args.image:
        encoder = ImageTextEncoder(download=args.download)
        products = load_products(limit=200)
        paths = [directory / "tier4/images" / f"{key}.png" for key in products.id]
        contents = [file_hash(p) for p in paths]
        save_artifact(
            "image_gallery",
            products.id.tolist(),
            contents,
            encoder.encode(paths, "image"),
            encoder.spec,
            "image",
        )
        texts = product_texts(products)
        save_artifact(
            "image_titles",
            products.id.tolist(),
            texts,
            encoder.encode(texts, "text"),
            encoder.spec,
            "text",
        )
        queries = [q for q in search_queries() if q["type"] == "photo"]
        texts = [q["text"] for q in queries]
        save_artifact(
            "image_queries",
            [q["id"] for q in queries],
            texts,
            encoder.encode(texts, "text"),
            encoder.spec,
            "text",
        )
        print("Prepared SigLIP 2: 200 image/text records and 50 text queries", flush=True)
    if args.reranker:
        print(
            Reranker(download=args.download).score(
                "warm coffee", ["A heated mug coaster", "A folding chair"]
            )
        )


if __name__ == "__main__":
    run_cli(main)
