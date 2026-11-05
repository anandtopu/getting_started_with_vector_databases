import math

import pytest

from common.bench.metrics import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    tie_aware_recall,
)


def test_metrics_against_hand_computed_values():
    judgments = {"a": 3, "b": 2}
    assert recall_at_k(["b", "x"], ["a", "b"], 2) == 0.5
    assert recall_at_k([], [], 2) is None
    assert precision_at_k(["a"], judgments, 2) == 0.5
    assert precision_at_k(["a", "a"], judgments, 2) == 0.5
    assert reciprocal_rank(["x", "b"], judgments) == 0.5
    assert ndcg_at_k(["a", "b"], judgments, 2) == 1.0
    assert ndcg_at_k(["b", "a"], judgments, 2) == pytest.approx(
        (3 + 7 / math.log2(3)) / (7 + 3 / math.log2(3))
    )
    assert ndcg_at_k([], {}, 2) is None


def test_ties_do_not_allow_missing_better_neighbors():
    reference = {
        "ordered": ["best", "tie1"],
        "required": ["best"],
        "boundary": ["tie1", "tie2", "tie3"],
    }
    assert tie_aware_recall(["best", "tie3"], reference, 2) == 1
    assert tie_aware_recall(["tie1", "tie2"], reference, 2) == 0.5
    assert tie_aware_recall(["best", "best"], reference, 2) == 0.5
