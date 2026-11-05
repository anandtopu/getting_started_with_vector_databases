"""Measure the recall cost of probing fewer lists.

Concepts: Measure the recall cost of probing fewer lists.
Run: uv run python modules/06_ivf/examples/03_measure.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import trial
from common.teaching import evidence


def main():
    observations = [trial("ivf", nlist=12, nprobe=p) for p in (1, 4, 12)]
    print(observations)
    evidence("lesson-06_ivf", {"observations": observations}, tier=2)


if __name__ == "__main__":
    main()
