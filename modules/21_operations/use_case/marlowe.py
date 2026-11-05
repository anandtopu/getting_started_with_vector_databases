"""Apply this module to Marlowe seller inventory.
Run: uv run python modules/21_operations/use_case/marlowe.py
CPU: seconds; frozen fixtures only, no model downloads or services.
"""

import tempfile
from pathlib import Path

import numpy as np

from common.ops.backup import Backups
from common.security.deletion import DeletionLedger
from common.stores.types import CollectionSpec, Record
from tinyvec import TinyVec


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        market = TinyVec()
        market.create_collection(CollectionSpec("seller-a", 2))
        market.upsert(
            [
                Record("listing-1", np.array([1.0, 0.0]), {"seller_id": "a"}),
                Record("listing-2", np.array([0.0, 1.0]), {"seller_id": "a"}),
            ]
        )
        backups = Backups(root / "backups")
        name = backups.create(market, watermark=2)
        ledger = DeletionLedger(root / "deletions.json")
        ledger.deny("a", ["listing-1"])
        restored, _ = backups.restore(name, ledger)
        assert [r.id for r in restored.records()] == ["listing-2"]
        print("Restored inventory after deletion replay:", [r.id for r in restored.records()])
        print("Purged snapshots:", backups.purge_containing("a", {"listing-1"}))


if __name__ == "__main__":
    main()
