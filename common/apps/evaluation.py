"""Application evaluations retain individual outputs, splits, timings and limitations."""

import time

import numpy as np
import pandas as pd

from common.apps.artifacts import load_artifact
from common.apps.clustering import review_themes
from common.apps.deduplication import calibrate, pair_scores, threshold_metrics
from common.apps.product_search import ProductSearch
from common.apps.rag import passage_recall, question_scope
from common.apps.recommendations import diversity, recommend, user_profile
from common.bench.metrics import (
    latency_summary,
    mean_defined,
    ndcg_at_k,
    precision_at_k,
    reciprocal_rank,
)
from common.data import load_products, load_vectors, records_from_products, search_queries
from common.embeddings import Reranker
from common.search.query_parser import parse_query
from common.settings import data_dir
from common.stores.ann import IndexedTinyVec
from common.stores.filters import matches, parse_filter
from common.stores.types import CollectionSpec, Record
from common.tier4 import open_photos, open_rag, review_data


def quality(ids, qrels):
    return {
        "ndcg10": ndcg_at_k(ids, qrels, 10),
        "mrr": reciprocal_rank(ids, qrels),
        "precision10": precision_at_k(ids, qrels, 10),
    }


def search_evaluation(database, *, rerank=False, repetitions=5):
    search = ProductSearch(database)
    queries = [q for q in search_queries() if q["type"] != "photo"]
    ids, parsed, _ = load_artifact(
        "queries_parsed", contents=[parse_query(q["text"]).text or q["text"] for q in queries]
    )
    query_vectors = dict(zip(ids, parsed, strict=True))
    frozen, _ = load_vectors(data_dir() / "query_embeddings.parquet")
    original = dict(zip([q["id"] for q in search_queries()], frozen, strict=True))
    reranker = Reranker() if rerank else None
    rows = []
    for q in queries:
        variants = {
            "v1_dense": ("dense", False, None),
            "v2_hybrid": ("hybrid", False, None),
            "v2_typo": ("hybrid", True, None),
        }
        if rerank:
            variants["v2_reranked"] = ("hybrid", True, reranker)
        for version, (mode, typo, ranker) in variants.items():
            vector = original[q["id"]] if version == "v1_dense" else query_vectors[q["id"]]
            result = search.search(q["text"], vector, mode=mode, typo=typo, reranker=ranker)
            found = [h.id for h in result.hits]
            condition = parse_filter(q["filter"])
            rows.append(
                {
                    "query": q["id"],
                    "type": q["type"],
                    "split": q["split"],
                    "version": version,
                    "ids": found,
                    **quality(found, q["qrels"]),
                    "filter_violations": sum(
                        not matches(h.metadata, condition) for h in result.hits
                    ),
                    "timings_ms": result.timings_ms,
                    "corrections": result.corrections,
                }
            )
    # Freeze the published hybrid policy before timing held-out requests.
    test = [q for q in queries if q["split"] == "test"]
    for q in test[:20]:
        search.search(q["text"], query_vectors[q["id"]])
    rng = np.random.default_rng(20261104)
    timings = []
    start = time.perf_counter()
    for _ in range(repetitions):
        for i in rng.permutation(len(test)):
            q = test[i]
            before = time.perf_counter()
            search.search(q["text"], query_vectors[q["id"]])
            timings.append((time.perf_counter() - before) * 1000)
    wall = time.perf_counter() - start
    summaries = []
    for version in sorted({r["version"] for r in rows}):
        for kind in sorted({r["type"] for r in rows}):
            selected = [
                r
                for r in rows
                if r["version"] == version and r["type"] == kind and r["split"] == "test"
            ]
            summaries.append(
                {
                    "version": version,
                    "type": kind,
                    "queries": len(selected),
                    **{
                        metric: mean_defined([r[metric] for r in selected])
                        for metric in ["ndcg10", "mrr", "precision10"]
                    },
                }
            )
    parser_correct = sum(parse_query(q["text"]).filter == q["filter"] for q in queries)
    return {
        "rows": rows,
        "held_out": summaries,
        "parser_exact_matches": parser_correct,
        "parser_queries": len(queries),
        "timing": {
            **latency_summary(timings),
            "queries": len(test),
            "repetitions": repetitions,
            "warmup": min(20, len(test)),
            "qps": len(timings) / wall,
            "embedding_excluded": True,
            "reranking_excluded": True,
        },
        "judgments": "Synthetic attribute rules, not human judgments. Photo queries are evaluated separately in Module 20.",
    }


def multilingual_evaluation(database):
    ids, vectors, meta = load_artifact("multilingual_products")
    qids, queries, _ = load_artifact("multilingual_queries")
    products = load_products(limit=len(ids))
    store = database.collection(
        "multilingual", records_from_products(products, vectors), meta["space"]
    )
    english, em = load_vectors(data_dir() / "embeddings_10k.parquet", products)
    baseline = database.collection(
        "english_comparison", records_from_products(products, english), em["space"]
    )
    frozen, _ = load_vectors(data_dir() / "query_embeddings.parquet")
    all_queries = search_queries()
    frozen = dict(zip([q["id"] for q in all_queries], frozen, strict=True))
    lookup = {q["id"]: q for q in all_queries}
    rows = []
    for key, vector in zip(qids, queries, strict=True):
        q = lookup[key]
        judged = {k: v for k, v in q["qrels"].items() if k in ids}
        for label, native, v, space in [
            ("Qwen", store, vector, meta["space"]),
            ("MiniLM", baseline, frozen[key], em["space"]),
        ]:
            found = [h.id for h in native.search(v, 10, space=space)]
            rows.append(
                {
                    "query": key,
                    "split": q["split"],
                    "model": label,
                    "ids": found,
                    **quality(found, judged),
                }
            )
    return {
        "catalog_rows": len(ids),
        "rows": rows,
        "held_out": {
            label: mean_defined(
                [r["ndcg10"] for r in rows if r["model"] == label and r["split"] == "test"]
            )
            for label in ["MiniLM", "Qwen"]
        },
    }


def rag_evaluation(database, *, generate=False):
    rag, qa, queries = open_rag(database)
    _, vectors, meta = load_artifact("rag_chunks")
    rows = []
    approximate = IndexedTinyVec(kind="ivf", nlist=8, nprobe=1, filter_policy="post", oversample=1)
    approximate.create_collection(CollectionSpec("rag_ann", vectors.shape[1], space=meta["space"]))
    approximate.upsert(
        [Record(c.id, v, c.metadata, c.text) for c, v in zip(rag.chunks, vectors, strict=True)]
    )
    approximate.build()
    narrow = IndexedTinyVec(kind="lsh", bits=10, tables=1, filter_policy="post", oversample=1)
    narrow.create_collection(CollectionSpec("rag_lsh", vectors.shape[1], space=meta["space"]))
    narrow.upsert(
        [Record(c.id, v, c.metadata, c.text) for c, v in zip(rag.chunks, vectors, strict=True)]
    )
    narrow.build()
    for q in qa:
        exact = rag.retrieve(q["question"], queries[q["id"]])
        ann = approximate.search(
            queries[q["id"]], 4, question_scope(q["question"]), space=meta["space"]
        )
        sparse_hits = narrow.search(
            queries[q["id"]], 4, question_scope(q["question"]), space=meta["space"]
        )
        rows.append(
            {
                "id": q["id"],
                "question": q["question"],
                "reference_answer": q["reference_answer"],
                "sources": q["source_passages"],
                "exact_recall": passage_recall(exact, q["source_passages"]),
                "ann_recall": passage_recall(ann, q["source_passages"]),
                "lsh_recall": passage_recall(sparse_hits, q["source_passages"]),
                "lsh_ids": [h.id for h in sparse_hits],
                "exact_ids": [h.id for h in exact],
                "ann_ids": [h.id for h in ann],
            }
        )
        if generate and int(q["id"].split("-")[1]) in {0, 1, 2, 20, 40, 60}:
            rows[-1]["generation"] = rag.answer(q["question"], exact)
            rows[-1]["ann_generation"] = rag.answer(q["question"], ann)
            rows[-1]["lsh_generation"] = rag.answer(q["question"], sparse_hits)
    approximate.close()
    narrow.close()
    return {
        "rows": rows,
        "exact_passage_recall4": float(np.mean([r["exact_recall"] for r in rows])),
        "ann_passage_recall4": float(np.mean([r["ann_recall"] for r in rows])),
        "lsh_passage_recall4": float(np.mean([r["lsh_recall"] for r in rows])),
        "lsh_config": {"bits": 10, "tables": 1, "filter_policy": "post"},
        "ann_config": {
            "kind": "ivf",
            "nlist": 8,
            "nprobe": 1,
            "filter_policy": "post",
            "oversample": 1,
        },
        "scope": "80 answerable synthetic questions. Generation on six stratified questions per index. Small diagnostic, not a population faithfulness estimate.",
        "empty_evidence": rag.answer("What is tomorrow's stock price?", []),
    }


def recommendation_evaluation(database):
    search = ProductSearch(database)
    vectors = {key: r.vector for key, r in search.by_id.items()}
    events = pd.read_parquet(data_dir() / "tier4/events_evaluation.parquet")
    events = events[events.product_id.isin(vectors)]
    cutoff = "2025-12-20T00:00:00Z"
    rows = []
    for user, group in list(events.groupby("user_id"))[:100]:
        profile, seen = user_profile(group.to_dict("records"), vectors, cutoff)
        future = (
            set(group.loc[(group.timestamp >= cutoff) & (group.action == "purchase"), "product_id"])
            - seen
        )
        if profile is None or not future:
            rows.append(
                {
                    "user": user,
                    "evaluated": False,
                    "reason": "No past profile or unseen future purchase",
                }
            )
            continue
        for weight in [1.0, 0.7, 0.3]:
            ids = recommend(search, profile, exclude=seen, relevance=weight)
            rows.append(
                {
                    "user": user,
                    "evaluated": True,
                    "weight": weight,
                    "ids": ids,
                    "future": sorted(future),
                    "recall10": len(set(ids) & future) / len(future),
                    "diversity": diversity(ids, vectors),
                    "seen_leaks": len(set(ids) & seen),
                }
            )
    pairs = pd.read_parquet(data_dir() / "tier4/duplicates.parquet")
    pairs = pairs[pairs.source_id.isin(vectors) & pairs.duplicate_id.isin(vectors)]
    development = pairs[pairs.split == "development"]
    test = pairs[pairs.split == "test"]
    assert not set(development.group_id) & set(test.group_id)
    calibration = calibrate(
        pair_scores(development.to_dict("records"), vectors), development.label.tolist()
    )
    tested = threshold_metrics(
        pair_scores(test.to_dict("records"), vectors), test.label.tolist(), calibration["threshold"]
    )
    reviews, matrix, _ = review_data()
    themes = review_themes(reviews.text.tolist(), matrix)
    return {
        "cutoff": cutoff,
        "recommendations": rows,
        "duplicates": {
            "development": calibration,
            "test": tested,
            "excluded_pairs": 2000 - len(pairs),
            "reason": "Only pairs with both IDs in the committed 10k catalog are scored",
        },
        "reviews": themes,
        "scope": "Synthetic behavior measures plumbing and policy trade-offs, not real conversion lift. Review themes and outliers have no human ground-truth labels.",
    }


def photo_evaluation(database):
    photos, images, _ = open_photos(database)
    qids, queries, _ = load_artifact("image_queries")
    lookup = {q["id"]: q for q in search_queries()}
    rows = []
    try:
        for key, vector in zip(qids, queries, strict=True):
            q = lookup[key]
            own = q["image"].split("/")[-1].removesuffix(".png")
            judgments = {k: v for k, v in q["qrels"].items() if k in photos.ids and k != own}
            for mode, query, weight in [
                ("text_to_image", vector, 1.0),
                ("photo", images[photos.ids.index(own)], 1.0),
                ("fused", vector, 0.7),
            ]:
                start = time.perf_counter()
                hits = photos.search(query, space=photos.space, image_weight=weight, exclude=[own])
                ids = [h.id for h in hits]
                rows.append(
                    {
                        "query": key,
                        "split": q["split"],
                        "mode": mode,
                        "ids": ids,
                        "self_excluded": own,
                        "eligible_relevant": len(judgments),
                        **quality(ids, judgments),
                        "ms": (time.perf_counter() - start) * 1000,
                    }
                )
    finally:
        photos.close()
    return {
        "rows": rows,
        "catalog_rows": len(images),
        "held_out": {
            mode: mean_defined(
                [r["ndcg10"] for r in rows if r["mode"] == mode and r["split"] == "test"]
            )
            for mode in ["text_to_image", "photo", "fused"]
        },
        "scope": "200 synthetic Pillow illustrations. Exact query image ID excluded. Repeated drawing templates still make this easier than photographs. No real-photo generalization claim.",
    }
