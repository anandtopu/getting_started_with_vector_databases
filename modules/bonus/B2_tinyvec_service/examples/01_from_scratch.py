"""Inspect write-ahead ordering and incomplete-tail recovery.
Concepts: durability and replay.
Run: uv run python modules/bonus/B2_tinyvec_service/examples/01_from_scratch.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""

import tempfile
from pathlib import Path

import numpy as np

from common.stores.types import CollectionSpec, Record
from tinyvec.durable import DurableTinyVec


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        spec = CollectionSpec("lesson", 2)
        with DurableTinyVec(root, spec) as store:
            print("acknowledged", store.upsert([Record("a", np.array([1.0, 0.0]))]))
            store.checkpoint()
        with (root / "mutations.jsonl").open("ab") as stream:
            stream.write(b"{incomplete")
        with DurableTinyVec(root, spec) as restored:
            assert restored.search([1, 0])[0].id == "a"
            print("recovered sequence", restored.wal.sequence)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
