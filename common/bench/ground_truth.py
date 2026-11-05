"""Independent exact reference: does not invoke the adapter being measured."""

import numpy as np

from common.stores.filters import matches, parse_filter


def neighbor_reference(
    vectors: np.ndarray,
    ids: list[str],
    metadata: list[dict],
    query: np.ndarray,
    k: int,
    metric: str,
    expression: dict | None = None,
    block_size: int = 2048,
) -> dict:
    filter = parse_filter(expression)
    eligible = [i for i, row in enumerate(metadata) if matches(row, filter)]
    winners: list[tuple[float, str]] = []
    for start in range(0, len(eligible), block_size):
        positions = eligible[start : start + block_size]
        block = vectors[positions].astype(np.float64)
        target = query.astype(np.float64)
        if metric == "cosine":
            block /= np.linalg.norm(block, axis=1, keepdims=True)
            target /= np.linalg.norm(target)
            values = np.einsum("ij,j->i", block, target)
        elif metric == "dot":
            values = np.einsum("ij,j->i", block, target)
        else:
            values = -np.sqrt(np.square(block - target).sum(axis=1))
        candidates = [
            (float(value), ids[pos]) for value, pos in zip(values, positions, strict=True)
        ]
        winners.extend(candidates)
    winners.sort(key=lambda pair: (-pair[0], pair[1]))
    ordered = [key for _, key in winners[:k]]
    if not ordered:
        return {"ordered": [], "required": [], "boundary": [], "tolerance": 0.0}
    cutoff = winners[min(k, len(winners)) - 1][0]
    tolerance = max(1e-7, abs(cutoff) * 1e-6)
    return {
        "ordered": ordered,
        "required": [key for score, key in winners if score > cutoff + tolerance],
        "boundary": [key for score, key in winners if abs(score - cutoff) <= tolerance],
        "tolerance": tolerance,
    }


def exact_neighbors(*args, **kwargs) -> list[str]:
    return neighbor_reference(*args, **kwargs)["ordered"]
