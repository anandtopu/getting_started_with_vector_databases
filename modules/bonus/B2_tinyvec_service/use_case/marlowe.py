"""Apply the bonus concept to Marlowe inventory and evaluation.
Run: uv run python modules/bonus/B2_tinyvec_service/use_case/marlowe.py
Expected: protected invariants and an explained result. CPU: seconds.
Needs: included data; B1 additionally requires the prepared Node toolchain.
"""

import tempfile
from pathlib import Path

import numpy as np

from common.stores.types import CollectionSpec, Record
from tinyvec.durable import DurableTinyVec


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        spec = CollectionSpec("seller-inventory", 2)
        with DurableTinyVec(root, spec) as store:
            store.upsert([Record("listing", np.array([1.0, 0.0]), {"seller_id": "a"})])
            store.checkpoint()
            store.delete(["listing"])
        with DurableTinyVec(root, spec) as restored:
            assert restored.search([1, 0]) == []
            print("Withdrawn listings stay withdrawn after checkpoint plus WAL replay.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
