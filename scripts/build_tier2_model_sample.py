"""Freeze a small Qwen Matryoshka sample and cross-encoder ranking for offline lessons.

Run: uv run --extra models python scripts/build_tier2_model_sample.py --download
CPU: several minutes. First run downloads the pinned weights to the course cache.
"""

import argparse
import json

import numpy as np

from common.data import product_texts
from common.io import atomic_json, file_hash
from common.settings import ROOT, cache_dir
from common.teaching import catalog


def main():
    import torch
    from huggingface_hub import snapshot_download
    from sentence_transformers import CrossEncoder, SentenceTransformer

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(2)
    pins = {
        r["name"]: r["sha"]
        for r in json.loads((ROOT / "research/models-2026-11-04.json").read_text())
    }

    def weights(name):
        return snapshot_download(
            name,
            revision=pins[name],
            cache_dir=cache_dir() / "models",
            allow_patterns=["*.json", "*.txt", "*.safetensors", "*.model", "*.jinja"],
            ignore_patterns=["onnx/*", "openvino/*", "onnx_*/*"],
            local_files_only=not args.download,
        )

    products, vectors, query, _ = catalog(128)
    texts = product_texts(products)
    question = "something to keep my coffee warm at my desk"
    model_name = "Qwen/Qwen3-Embedding-0.6B"
    model = SentenceTransformer(weights(model_name), device="cpu", trust_remote_code=False)
    output = ROOT / "data" / "tier2"
    output.mkdir(parents=True, exist_ok=True)
    embedded = model.encode(texts, batch_size=8, normalize_embeddings=True)
    prompt = "Instruct: Given a web search query, retrieve relevant passages that answer the query\nQuery: "
    q = model.encode([prompt + question], normalize_embeddings=True)
    np.savez_compressed(
        output / "matryoshka.npz",
        documents=embedded,
        query=q[0],
        ids=np.asarray(products.id, dtype=str),
    )
    del model
    name = "cross-encoder/ms-marco-MiniLM-L6-v2"
    from common.embeddings import frozen_query
    from common.settings import data_dir

    _, meta = frozen_query("q000", data_dir())
    from common.data import search_queries

    query_text = next(r["text"] for r in search_queries() if r["id"] == "q000")
    candidates = np.argsort(-(vectors @ query))[:12]
    encoder = CrossEncoder(weights(name), device="cpu", trust_remote_code=False)
    scores = encoder.predict([(query_text, texts[i]) for i in candidates])
    atomic_json(
        output / "reranking.json",
        {
            "model": name,
            "revision": pins[name],
            "query": query_text,
            "query_id": "q000",
            "source_space": meta["space"],
            "candidates": [
                {"id": products.id.iloc[i], "score": float(s)}
                for i, s in zip(candidates, scores, strict=True)
            ],
        },
    )
    atomic_json(
        output / "manifest.json",
        {
            "model": model_name,
            "revision": pins[model_name],
            "query": question,
            "query_prefix": prompt,
            "rows": len(texts),
            "dimensions": embedded.shape[1],
            "products_source": "first 128 rows of products_10k.parquet",
            "sha256": {f: file_hash(output / f) for f in ["matryoshka.npz", "reranking.json"]},
        },
    )


if __name__ == "__main__":
    main()
