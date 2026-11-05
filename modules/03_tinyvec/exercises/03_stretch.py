"""Persist vectors, metadata and stable IDs as a complete snapshot.

Run: uv run python modules/03_tinyvec/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/03_tinyvec/exercises/03_stretch.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import json
import tempfile
from pathlib import Path

import numpy as np

from common.stores.types import Record


def solve(records: list[Record], path: Path) -> list[Record]:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    path.mkdir(parents=True, exist_ok=True)
    (path / "ids.json").write_text(json.dumps([r.id for r in records]), encoding="utf-8")
    return [Record(r.id, r.vector.copy()) for r in records]


def main() -> None:
    with tempfile.TemporaryDirectory() as folder:
        print(solve([Record("mug", np.array([1.0, 0.2]), {"price": 20})], Path(folder)))


if __name__ == "__main__":
    main()
