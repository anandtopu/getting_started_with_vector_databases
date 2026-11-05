"""Run the same workload against any registered foundation adapter."""

import random
import sys
import tempfile
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from threadpoolctl import threadpool_limits

from common.bench.config import BenchConfig
from common.bench.ground_truth import neighbor_reference
from common.bench.hardware import hardware, provenance
from common.bench.metrics import (
    latency_summary,
    mean_defined,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    tie_aware_recall,
)
from common.bench.resources import MemorySampler, disk_bytes
from common.data import (
    load_products,
    load_vectors,
    product_texts,
    records_from_products,
    search_queries,
)
from common.embeddings import HashEncoder
from common.generation import judgments, product
from common.io import atomic_json, digest, file_hash
from common.settings import ROOT, cache_dir, data_dir
from common.stores.registry import make_store
from common.stores.types import CollectionSpec


def workload(config: BenchConfig) -> tuple:
    if config.dataset == "fixture":
        products = pd.DataFrame([product(i, config.seed) for i in range(config.limit)])
        encoder = HashEncoder()
        vectors = encoder.encode(product_texts(products))
        queries = judgments(products.to_dict(orient="records"))
        query_vectors = encoder.encode([q["text"] for q in queries], "query")
        metadata = {
            "space": encoder.spec.space,
            "storage_dtype": "float32",
            "model": "hash-v1; mechanics only",
        }
        data_hash = digest(products.to_dict(orient="records"))
    else:
        products = load_products(limit=config.limit)
        vectors, metadata = load_vectors(data_dir() / "embeddings_10k.parquet", products)
        queries = search_queries()
        query_vectors, query_metadata = load_vectors(data_dir() / "query_embeddings.parquet")
        query_ids = pq.read_table(data_dir() / "query_embeddings.parquet", columns=["id"])[
            "id"
        ].to_pylist()
        positions = {key: i for i, key in enumerate(query_ids)}
        query_vectors = query_vectors[[positions[q["id"]] for q in queries]]
        if metadata["space"] != query_metadata["space"]:
            raise ValueError("Product and query embeddings come from different spaces")
        data_hash = digest(
            {
                "products": file_hash(data_dir() / "products_10k.parquet"),
                "vectors": metadata["sha256"],
                "limit": len(products),
            }
        )
    selected = [
        i
        for i, query in enumerate(queries)
        if query["type"] in config.query_types
        and (config.split == "all" or query["split"] == config.split)
    ]
    random.Random(config.seed).shuffle(selected)
    selected = selected[: config.queries]
    if not selected:
        raise ValueError("No queries match the requested split and query types")
    ids = set(products["id"])
    chosen = [
        {
            **queries[i],
            "qrels": {key: grade for key, grade in queries[i]["qrels"].items() if key in ids},
        }
        for i in selected
    ]
    return products, vectors, chosen, query_vectors[selected], metadata, data_hash


def run_benchmark(config: BenchConfig, output: Path | None = None) -> dict:
    output = output or ROOT / "results"
    products, vectors, queries, query_vectors, embedding, data_hash = workload(config)
    records = records_from_products(products, vectors)
    ids = [r.id for r in records]
    metadata = [r.metadata for r in records]
    cache_dir().mkdir(parents=True, exist_ok=True)
    with (
        tempfile.TemporaryDirectory(prefix="bench-", dir=cache_dir()) as temporary,
        threadpool_limits(limits=config.threads),
    ):
        directory = Path(temporary)
        # Chroma's native SQLite pool may release handles asynchronously on Windows.
        # Give it a course-owned persistent directory and isolate runs by collection.
        db_path = (
            cache_dir() / "tier3/chroma" if config.backend == "chroma" else directory / "store.db"
        )
        store = make_store(config.backend, path=db_path, **config.parameters)
        spec = CollectionSpec("marlowe", vectors.shape[1], config.metric, embedding["space"])
        samples: list[dict] = []
        repeat_qps: list[float] = []
        try:
            with MemorySampler() as memory:
                start = time.perf_counter()
                store.create_collection(spec)
                store.upsert(records)
                insertion_seconds = time.perf_counter() - start
                start = time.perf_counter()
                if hasattr(store, "build"):
                    store.build()
                build_seconds = time.perf_counter() - start
                index_payload = store.index.payload_bytes if config.backend == "ann" else None

                def retrieve(position):
                    args = (query_vectors[position], config.k, queries[position]["filter"])
                    if config.retrieval == "hybrid":
                        return store.hybrid_search(
                            queries[position]["text"], *args, space=spec.space
                        )
                    return store.search(*args, space=spec.space)

                for i in range(config.warmup):
                    position = i % len(queries)
                    retrieve(position)
                for repeat in range(config.repetitions):
                    order = list(range(len(queries)))
                    random.Random(config.seed + repeat).shuffle(order)
                    start_repeat = time.perf_counter()
                    for position in order:
                        start = time.perf_counter_ns()
                        hits = retrieve(position)
                        elapsed = (time.perf_counter_ns() - start) / 1e6
                        samples.append(
                            {
                                "query_id": queries[position]["id"],
                                "repeat": repeat,
                                "latency_ms": elapsed,
                                "ids": [hit.id for hit in hits],
                            }
                        )
                    repeat_qps.append(len(order) / (time.perf_counter() - start_repeat))
                store.save(directory / "snapshot")
                persisted_bytes = disk_bytes(directory / "snapshot")
            # Quality computation is outside all measured request intervals.
            truth = {
                q["id"]: neighbor_reference(
                    vectors, ids, metadata, v, config.k, config.metric, q["filter"]
                )
                for q, v in zip(queries, query_vectors, strict=True)
            }
            lookup = {q["id"]: q for q in queries}
            for sample in samples:
                q = lookup[sample["query_id"]]
                found = sample["ids"]
                sample.update(
                    {
                        "query_type": q["type"],
                        "recall_at_k": tie_aware_recall(found, truth[q["id"]], config.k),
                        "strict_id_recall_at_k": recall_at_k(
                            found, truth[q["id"]]["ordered"], config.k
                        ),
                        "precision_at_k": precision_at_k(found, q["qrels"], config.k),
                        "mrr": reciprocal_rank(found, q["qrels"]),
                        "ndcg_at_k": ndcg_at_k(found, q["qrels"], config.k),
                    }
                )
        finally:
            store.close()
    quality_keys = ["recall_at_k", "strict_id_recall_at_k", "precision_at_k", "mrr", "ndcg_at_k"]
    summary = {
        **latency_summary([s["latency_ms"] for s in samples]),
        **{key: mean_defined([s[key] for s in samples]) for key in quality_keys},
        "qps": float(np.mean(repeat_qps)),
        "qps_std": float(np.std(repeat_qps, ddof=1)) if len(repeat_qps) > 1 else 0.0,
        "insertion_seconds": insertion_seconds,
        "index_build_seconds": build_seconds,
        "persisted_bytes": persisted_bytes,
        "index_payload_bytes": index_payload,
        "errors": 0,
        "error_rate": 0.0,
    }
    timestamp = datetime.now(UTC)
    run_id = f"{config.name}-{timestamp:%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}"
    machine = hardware()
    usage = memory.report()
    if config.backend in {
        "pgvector",
        "qdrant",
        "weaviate",
        "milvus",
        "elasticsearch",
        "redis",
        "mongodb",
        "vespa",
    } and not config.parameters.get("local"):
        usage["server_memory_reason"] = (
            "Separate server. This sampler measures the Python client only."
        )
    report = {
        "format": 1,
        "run_id": run_id,
        "created_at": timestamp.isoformat(),
        "config": config.model_dump(),
        "config_sha256": digest(config.model_dump()),
        "hardware": machine,
        "hardware_id": digest(machine)[:12],
        "provenance": provenance(),
        "command": [sys.executable, *sys.argv],
        "embedding": embedding,
        "dataset_sha256": data_hash,
        "queries_sha256": digest(queries),
        "query_count": len(queries),
        "record_count": len(records),
        "summary": summary,
        "memory": usage,
        "repeat_qps": repeat_qps,
        "by_query_type": {
            kind: {
                key: mean_defined([s[key] for s in samples if s["query_type"] == kind])
                for key in quality_keys
            }
            for kind in sorted({q["type"] for q in queries})
        },
        "samples": samples,
        "ground_truth": truth,
        "method": {
            "recall_semantics": "tie-aware-v1; strict ID recall is also reported",
            "quality": "synthetic attribute judgments; not human-reviewed",
            "ground_truth": "independent blocked exact search with float64 accumulation on the stored vector values; ID tie-break",
            "embedding_latency": "excluded; precomputed vectors",
            "concurrency": 1,
            "qps": "mean of repeated serial completed requests / wall seconds; includes per-request loop bookkeeping",
            "empty_eligible": "recall is null and excluded from mean",
            "warm_cache": True,
            "percentile_warning": "p99 is unstable for small samples; inspect sample count",
            "photo_queries": "excluded: frozen text surrogates are not image evaluation",
        },
    }
    atomic_json(output / "runs" / f"{run_id}.json", report)
    return report
