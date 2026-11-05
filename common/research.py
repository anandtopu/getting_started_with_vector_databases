"""Small reproducible experiments; never substitutes laptop results for paper claims."""

import json
import time
import uuid
from datetime import UTC, datetime

import numpy as np
from threadpoolctl import threadpool_limits

from common.bench.hardware import hardware, provenance
from common.data import load_vectors
from common.errors import CourseError
from common.io import atomic_json, file_hash
from common.settings import ROOT, data_dir
from common.teaching import catalog


def record(name, observations, command):
    path = ROOT / "results/bonus" / f"{name}-{uuid.uuid4().hex[:8]}.json"
    atomic_json(
        path,
        {
            "created_at": datetime.now(UTC).isoformat(),
            "hardware": hardware(),
            "provenance": provenance(),
            "command": command,
            "observations": observations,
        },
    )
    return path


def public_benchmark():
    import faiss

    folder = data_dir() / "benchmarks/fashion-mnist"
    if not (folder / "subset.npz").exists():
        raise CourseError(
            "Prepare the licensed dataset: python scripts/download_benchmarks.py --download. See scripts/check_env.py."
        )
    manifest = json.loads((folder / "subset.manifest.json").read_text(encoding="utf8"))
    if file_hash(folder / "subset.npz") != manifest["sha256"]:
        raise ValueError("Public benchmark subset checksum changed")
    with np.load(folder / "subset.npz", allow_pickle=False) as archive:
        base = np.ascontiguousarray(archive["base"][:3000], dtype=np.float32)
        queries = np.ascontiguousarray(archive["queries"][:120], dtype=np.float32)
    if len(base) < 1000 or len(queries) < 120:
        raise CourseError("Recreate the default benchmark subset (10k base, 1k queries)")
    faiss.omp_set_num_threads(1)
    with threadpool_limits(limits=1):
        exact = faiss.IndexFlatL2(base.shape[1])
        exact.add(base)
        distances, truth = exact.search(queries, 10)
        start = time.perf_counter()
        index = faiss.IndexHNSWFlat(base.shape[1], 24)
        index.hnsw.efConstruction = 80
        index.add(base)
        build = time.perf_counter() - start

        def trial(ef, selection):
            index.hnsw.efSearch = ef
            timings = []
            recalls = []
            for _ in range(3):
                for i in selection:
                    start = time.perf_counter()
                    _, ids = index.search(queries[i : i + 1], 10)
                    timings.append((time.perf_counter() - start) * 1000)
                    # Ties in pixel-space data count against the exact distance boundary.
                    actual = ((base[ids[0]] - queries[i]) ** 2).sum(axis=1)
                    recalls.append(float(np.mean(actual <= distances[i, -1] + 1e-4)))
            return {
                "recall10": float(np.mean(recalls)),
                "p95_ms": float(np.percentile(timings, 95)),
                "samples": len(timings),
                "latencies_ms": timings,
            }

        development = {ef: trial(ef, range(60)) for ef in [10, 32, 64]}
        feasible = [ef for ef, result in development.items() if result["recall10"] >= 0.95]
        chosen = min(feasible) if feasible else None
        heldout = trial(chosen, range(60, 120)) if chosen else None
    return {
        "dataset": manifest,
        "base_rows": len(base),
        "query_rows": len(queries),
        "metric": "squared L2 on pixels, not learned image embeddings",
        "development": development,
        "chosen_efSearch": chosen,
        "heldout": heldout,
        "build_seconds": build,
        "serialized_bytes": len(faiss.serialize_index(index)),
        "exact_first_ids": truth[0].tolist(),
        "scope": "Protocol reproduction on a licensed subset. Not a reproduction of a paper's hardware or headline numbers. FAISS default HNSW RNG; one thread.",
    }


def rabitq_experiment(native=False):
    from tinyvec.rabitq import RaBitQ

    _, base, _, metadata = catalog(1000)
    queries, qmeta = load_vectors(data_dir() / "query_embeddings.parquet")
    assert metadata["space"] == qmeta["space"]
    queries = queries[:40]
    base = base / np.linalg.norm(base, axis=1, keepdims=True)
    queries = queries / np.linalg.norm(queries, axis=1, keepdims=True)
    exact = np.maximum(0, 2 - 2 * (queries @ base.T))
    boundary = np.sort(exact, axis=1)[:, 9]
    rows = []
    with threadpool_limits(limits=1):
        for seed in [41, 42, 43]:
            start = time.perf_counter()
            index = RaBitQ(base, seed)
            build = time.perf_counter() - start
            approximate = []
            rescored = []
            errors = []
            times = []
            for i, q in enumerate(queries):
                start = time.perf_counter()
                estimated = index.distances(q)
                candidates = np.argsort(estimated, kind="stable")[:100]
                candidate_distances = ((base[candidates] - q) ** 2).sum(axis=1)
                best = candidates[np.argsort(candidate_distances, kind="stable")[:10]]
                times.append((time.perf_counter() - start) * 1000)
                approximate.append(float(np.mean(exact[i, candidates[:10]] <= boundary[i] + 1e-5)))
                rescored.append(float(np.mean(exact[i, best] <= boundary[i] + 1e-5)))
                errors.append(float(np.mean(np.abs(estimated - exact[i]))))
            rows.append(
                {
                    "seed": seed,
                    "build_seconds": build,
                    "payload_bytes": index.payload_bytes,
                    "retained_float_bytes": base.nbytes,
                    "recall10": float(np.mean(approximate)),
                    "rescored_recall10": float(np.mean(rescored)),
                    "mean_absolute_squared_distance_error": float(np.mean(errors)),
                    "p95_ms": float(np.percentile(times, 95)),
                    "queries": len(queries),
                }
            )
        comparisons = []
        if native:
            import faiss

            faiss.omp_set_num_threads(1)
            for factory in ["Flat", "RR384,RaBitQ", "RR384,RaBitQ4"]:
                start = time.perf_counter()
                index = faiss.index_factory(384, factory, faiss.METRIC_L2)
                index.train(base)
                index.add(base)
                build = time.perf_counter() - start
                index.search(queries[:1], 10)
                start = time.perf_counter()
                _, ids = index.search(queries, 10)
                elapsed = time.perf_counter() - start
                recalls = [
                    float(np.mean(exact[i, found] <= boundary[i] + 1e-5))
                    for i, found in enumerate(ids)
                ]
                comparisons.append(
                    {
                        "factory": factory,
                        "recall10": float(np.mean(recalls)),
                        "build_seconds": build,
                        "batch_seconds": elapsed,
                        "queries": len(queries),
                        "serialized_bytes": len(faiss.serialize_index(index)),
                    }
                )
    return {
        "artifact_sha256": file_hash(data_dir() / "embeddings_10k.parquet"),
        "query_sha256": file_hash(data_dir() / "query_embeddings.parquet"),
        "model_space": metadata["space"],
        "scratch": rows,
        "native": comparisons,
        "scope": "40 frozen queries, distance-boundary recall, 100-candidate exact rescoring retains full vectors. Scratch dense unpacking and native SIMD timings have different scopes. No theoretical-bound reproduction or held-out parameter selection claimed.",
    }
