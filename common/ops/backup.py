"""Immutable owned snapshots, checksum validation, deletion replay and explicit publication."""

import json
import shutil
import uuid
from datetime import UTC, datetime

from common.io import atomic_json, file_hash
from tinyvec import TinyVec


class Backups:
    def __init__(self, root):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        marker = self.root / "owner.json"
        if marker.exists():
            if json.loads(marker.read_text())["owner"] != "marlowe-tier5":
                raise ValueError("Backup directory has another owner")
        elif any(self.root.iterdir()):
            raise ValueError("Refuse a nonempty unowned backup directory")
        else:
            atomic_json(marker, {"owner": "marlowe-tier5"})

    def checked(self, name):
        path = (self.root / name).resolve()
        if path.parent != self.root or not name.startswith("snapshot-"):
            raise ValueError("Expected an owned snapshot name")
        return path

    def create(self, store, *, watermark=0):
        name = "snapshot-" + uuid.uuid4().hex
        path = self.checked(name)
        # SQLite's native save is a database file; logical portable backups use records.
        if hasattr(store, "records"):
            logical = TinyVec()
            logical.create_collection(store.spec)
            logical.upsert(store.records())
            logical.save(path)
        else:
            store.save(path)
        atomic_json(
            path / "backup.json",
            {
                "owner": "marlowe-tier5",
                "created_at": datetime.now(UTC).isoformat(),
                "watermark": watermark,
                "snapshot_sha256": file_hash(path / "snapshot.json"),
            },
        )
        return name

    def restore(self, name, ledger):
        path = self.checked(name)
        manifest = json.loads((path / "backup.json").read_text())
        if (
            manifest["owner"] != "marlowe-tier5"
            or file_hash(path / "snapshot.json") != manifest["snapshot_sha256"]
        ):
            raise ValueError("Corrupt snapshot manifest")
        store = TinyVec.load(path)
        ledger.apply(store)
        return store, manifest

    def purge_containing(self, tenant, ids):
        removed = []
        for path in self.root.glob("snapshot-*"):
            owned = self.checked(path.name)
            manifest = json.loads((owned / "backup.json").read_text())
            if manifest.get("owner") != "marlowe-tier5":
                raise ValueError("Unowned backup")
            rows = json.loads((owned / "snapshot.json").read_text())["records"]
            if any(
                r["id"] in ids
                and r["metadata"].get("seller_id", r["metadata"].get("tenant")) == tenant
                for r in rows
            ):
                # The resolved target is a direct child of the explicit owned root.
                shutil.rmtree(owned)
                removed.append(path.name)
        return removed
