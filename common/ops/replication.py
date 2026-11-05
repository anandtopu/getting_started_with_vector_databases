"""Deterministic simulation of replica lag and quorum trade-offs, never latency evidence."""

import hashlib


def shard_for(key: str, shards: int) -> int:
    if shards < 1:
        raise ValueError("Need at least one shard")
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "little") % shards


class ReplicaSimulation:
    def __init__(self, count=3):
        self.replicas = [{} for _ in range(count)]
        self.pending = []
        self.alive = set(range(count))
        self.version = 0

    def write(self, key, value, acknowledgements=1):
        if not 1 <= acknowledgements <= len(self.replicas):
            raise ValueError("Invalid quorum")
        if len(self.alive) < acknowledgements:
            raise RuntimeError("Write unavailable: insufficient live replicas")
        self.version += 1
        ready = sorted(self.alive)[:acknowledgements]
        for i in ready:
            self.replicas[i][key] = (self.version, value)
        self.pending.extend(
            (i, key, self.version, value) for i in range(len(self.replicas)) if i not in ready
        )
        return self.version

    def tick(self):
        pending, self.pending = self.pending, []
        for i, key, version, value in pending:
            if i not in self.alive:
                self.pending.append((i, key, version, value))
            elif self.replicas[i].get(key, (0, None))[0] < version:
                self.replicas[i][key] = (version, value)

    def read(self, replica, key):
        if replica not in self.alive:
            raise RuntimeError("Replica unavailable")
        return self.replicas[replica].get(key)
