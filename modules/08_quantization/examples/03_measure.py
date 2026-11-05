"""Measure code bytes, oversampling and trained prefix rankings.

Concepts: Measure code bytes, oversampling and trained prefix rankings.
Run: uv run python modules/08_quantization/examples/03_measure.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import prefix_results, trial
from common.teaching import evidence


def main():
    observations = {
        "compression": [
            trial(kind, oversample=s) for kind in ("scalar", "binary", "pq") for s in (1, 8)
        ],
        "qwen_prefixes": prefix_results(),
    }
    print(observations)
    evidence("lesson-08_quantization", {"observations": observations}, tier=2)


if __name__ == "__main__":
    main()
