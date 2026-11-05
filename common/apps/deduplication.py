"""Calibrate duplicate thresholds on development families, then freeze for test."""

import numpy as np

from common.embeddings import normalize


def pair_scores(pairs, vectors_by_id):
    return np.asarray(
        [
            float(
                normalize(vectors_by_id[p["source_id"]])
                @ normalize(vectors_by_id[p["duplicate_id"]])
            )
            for p in pairs
        ]
    )


def threshold_metrics(scores, labels, threshold: float) -> dict:
    scores, labels = np.asarray(scores), np.asarray(labels, dtype=bool)
    if scores.shape != labels.shape or not np.isfinite(scores).all():
        raise ValueError("Finite aligned scores and labels required")
    predicted = scores >= threshold
    tp, fp, fn = (
        int((predicted & labels).sum()),
        int((predicted & ~labels).sum()),
        int((~predicted & labels).sum()),
    )
    precision, recall = tp / max(1, tp + fp), tp / max(1, tp + fn)
    return {
        "threshold": float(threshold),
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(1e-12, precision + recall),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "pairs": len(scores),
    }


def calibrate(scores, labels) -> dict:
    if len(scores) == 0:
        raise ValueError("Development pairs cannot be empty")
    candidates = [*np.unique(scores), np.nextafter(float(np.max(scores)), np.inf)]
    return max(
        (threshold_metrics(scores, labels, t) for t in candidates),
        key=lambda m: (m["f1"], m["precision"], m["threshold"]),
    )
