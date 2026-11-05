"""Durable deny-before-delete ledger, replayed before serving restored data."""

import json
from threading import RLock

from common.io import atomic_json


class DeletionLedger:
    def __init__(self, path):
        self.path = path
        self.lock = RLock()
        self.entries = (
            json.loads(path.read_text(encoding="utf8"))
            if path.exists()
            else {"format": 1, "generation": 0, "tenants": {}}
        )
        if self.entries.get("format") != 1:
            raise ValueError("Unknown deletion ledger format")

    @property
    def generation(self):
        return self.entries["generation"]

    def denied(self, tenant):
        return set(self.entries["tenants"].get(tenant, []))

    def deny(self, tenant, ids):
        with self.lock:
            previous = self.denied(tenant)
            next_ids = previous | set(ids)
            if next_ids != previous:
                updated = json.loads(json.dumps(self.entries))
                updated["tenants"][tenant] = sorted(next_ids)
                updated["generation"] += 1
                atomic_json(self.path, updated)
                self.entries = updated
            return self.generation

    def apply(self, store):
        rows = store.records()
        doomed = [
            r.id
            for r in rows
            if r.id in self.denied(r.metadata.get("seller_id", r.metadata.get("tenant", "")))
        ]
        store.delete(doomed)
        return doomed
