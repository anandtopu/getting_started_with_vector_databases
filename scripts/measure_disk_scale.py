"""Measure a million generated vectors without allocating a full float matrix.
Run: uv run python scripts/measure_disk_scale.py --rows 1000000
CPU: seconds to minutes, default 32 MB of codes and bounded generation blocks. No models or Docker.
"""

import argparse
import tempfile
from pathlib import Path

from common.settings import cache_dir
from common.teaching import evidence
from tinyvec.mmap import experiment


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--dimensions", type=int, default=32)
    args = parser.parse_args()
    parent = cache_dir() / "tier2"
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=parent) as tmp:
        result = experiment(Path(tmp), args.rows, args.dimensions)
    print(result)
    evidence("disk-scale", result, tier=2)


if __name__ == "__main__":
    main()
