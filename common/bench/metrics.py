"""Metrics from their definitions: relevance judgments are distinct from ANN ground truth."""

import math
from collections.abc import Mapping, Sequence

import numpy as np


def recall_at_k(found: Sequence[str], truth: Sequence[str], k: int) -> float | None:
    relevant = set(truth[:k])
    return len(set(found[:k]) & relevant) / len(relevant) if relevant else None


def tie_aware_recall(found: Sequence[str], reference: dict, k: int) -> float | None:
    size = len(reference["ordered"])
    if not size:
        return None
    selected = set(found[:k])
    required = set(reference["required"])
    boundary = set(reference["boundary"])
    # Missing a strictly closer item cannot be compensated for by an extra boundary tie.
    return (len(selected & required) + min(size - len(required), len(selected & boundary))) / size


def precision_at_k(found: Sequence[str], judgments: Mapping[str, int], k: int) -> float:
    if k < 1:
        raise ValueError("k must be positive")
    return sum(judgments.get(key, 0) > 0 for key in dict.fromkeys(found[:k])) / k


def reciprocal_rank(found: Sequence[str], judgments: Mapping[str, int]) -> float:
    return next((1.0 / rank for rank, key in enumerate(found, 1) if judgments.get(key, 0) > 0), 0.0)


def ndcg_at_k(found: Sequence[str], judgments: Mapping[str, int], k: int) -> float | None:
    def dcg(grades: Sequence[int]) -> float:
        return sum(
            (2**grade - 1) / math.log2(position + 2) for position, grade in enumerate(grades[:k])
        )

    ideal = dcg(sorted(judgments.values(), reverse=True))
    seen = set()
    grades = []
    for key in found[:k]:
        grades.append(judgments.get(key, 0) if key not in seen else 0)
        seen.add(key)
    return dcg(grades) / ideal if ideal else None


def mean_defined(values: Sequence[float | None]) -> float | None:
    defined = [value for value in values if value is not None]
    return float(np.mean(defined)) if defined else None


def latency_summary(milliseconds: Sequence[float]) -> dict:
    if not milliseconds:
        raise ValueError("Need measured query latencies")
    return {
        "p50_ms": float(np.percentile(milliseconds, 50)),
        "p95_ms": float(np.percentile(milliseconds, 95)),
        "p99_ms": float(np.percentile(milliseconds, 99)),
        "samples": len(milliseconds),
    }
