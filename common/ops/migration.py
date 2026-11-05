"""Atomic application routing couples a collection generation with its encoder space."""

import json
from threading import RLock

from common.io import atomic_json


class ModelRouter:
    def __init__(self, path):
        self.path = path
        self.lock = RLock()
        self.active = json.loads(path.read_text(encoding="utf8")) if path.exists() else None

    def publish(self, collection, space, *, ready, measured_recall, minimum_recall):
        if not ready or not 0 <= minimum_recall <= measured_recall <= 1:
            raise ValueError("Migration quality/readiness gate failed")
        with self.lock:
            state = {"collection": collection, "space": space, "previous": self.active}
            atomic_json(self.path, state)
            self.active = state
            return state

    def rollback(self):
        with self.lock:
            if not self.active or not self.active.get("previous"):
                raise ValueError("No rollback generation")
            previous = self.active["previous"]
            atomic_json(self.path, previous)
            self.active = previous

    def route(self, query_space):
        with self.lock:
            if not self.active or self.active["space"] != query_space:
                raise ValueError("Query encoder and active collection differ")
            return self.active["collection"]
