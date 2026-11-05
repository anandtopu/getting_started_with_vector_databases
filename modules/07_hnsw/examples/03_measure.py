"""Measure beam width and graph payload.

Concepts: Measure beam width and graph payload.
Run: uv run python modules/07_hnsw/examples/03_measure.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import trial
from common.teaching import evidence


def main():
    observations = [
        trial("hnsw", M=6, efConstruction=32, efSearch=e, oversample=1) for e in (10, 24, 64)
    ]
    print(observations)
    evidence("lesson-07_hnsw", {"observations": observations}, tier=2)


if __name__ == "__main__":
    main()
