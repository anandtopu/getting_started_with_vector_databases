"""Compute an independent distance boundary and distinguish approximation from relevance.
Concepts: ground truth and evaluation.
Run: uv run python modules/bonus/B3_research_benchmarks/examples/01_from_scratch.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""

import numpy as np


def main() -> None:
    base = np.array([[0, 0], [1, 0], [0, 1], [2, 2]], dtype=float)
    query = np.array([0.9, 0.1])
    distances = ((base - query) ** 2).sum(axis=1)
    truth = np.argsort(distances, kind="stable")[:2]
    candidate = np.array([1, 3])
    recall = np.mean(distances[candidate] <= distances[truth[-1]])
    assert recall == 0.5
    print({"truth": truth.tolist(), "candidate": candidate.tolist(), "recall": recall})
    print("No category labels are needed for ANN recall; relevance needs independent judgments.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
