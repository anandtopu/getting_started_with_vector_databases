"""Measure how hash table count changes coverage.

Concepts: Measure how hash table count changes coverage.
Run: uv run python modules/05_ann_lsh/examples/03_measure.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import trial
from common.teaching import evidence


def main():
    observations = [trial("lsh", tables=t, bits=6) for t in (1, 4, 12)]
    print(observations)
    evidence("lesson-05_ann_lsh", {"observations": observations}, tier=2)


if __name__ == "__main__":
    main()
