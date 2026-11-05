"""Read bounded pages of scalar codes from disk.

Concepts: Read bounded pages of scalar codes from disk.
Run: uv run python modules/09_disk_scale/examples/01_from_scratch.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

import tempfile
from pathlib import Path

from tinyvec.mmap import experiment


def main():
    with tempfile.TemporaryDirectory() as directory:
        result = experiment(Path(directory), rows=8193, dimensions=32, block=1024)
    print("code bytes", result["bytes_per_scan"], "recall", result["recall_at_10"])
    assert result["bytes_per_scan"] == 8193 * 32


if __name__ == "__main__":
    main()
