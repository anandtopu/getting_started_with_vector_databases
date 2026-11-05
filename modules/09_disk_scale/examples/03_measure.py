"""Measure a million generated product vectors with bounded allocation.

Concepts: Measure a million generated product vectors with bounded allocation.
Run: uv run python modules/09_disk_scale/examples/03_measure.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from scripts.measure_disk_scale import main as measure


def main():
    measure()


if __name__ == "__main__":
    main()
