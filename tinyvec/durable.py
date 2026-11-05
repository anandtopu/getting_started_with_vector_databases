"""Single-writer persistent TinyVec; validated writes are logged before becoming visible."""

import json
import uuid
from dataclasses import asdict
from threading import RLock

import numpy as np

from common.io import atomic_json
from common.stores.types import CollectionSpec, Record, checked_record
from tinyvec import TinyVec
from tinyvec.wal import ProcessLock, WriteAheadLog


class DurableTinyVec:
    def __init__(self, root, spec):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.owner = ProcessLock(self.root / "writer.lock")
        self.closed = False
        try:
            schema = self.root / "schema.json"
            if schema.exists():
                if CollectionSpec(**json.loads(schema.read_text(encoding="utf8"))) != spec:
                    raise ValueError("Persistent collection schema differs")
            else:
                if any(p.name != "writer.lock" for p in self.root.iterdir()):
                    raise ValueError("Refuse an unrecognized nonempty data directory")
                atomic_json(schema, asdict(spec))
            self.store = TinyVec()
            self.store.create_collection(spec)
            watermark = 0
            if (self.root / "checkpoint.json").exists():
                pointer = json.loads((self.root / "checkpoint.json").read_text(encoding="utf8"))
                folder = (self.root / pointer["directory"]).resolve()
                if folder.parent != self.root or not folder.name.startswith("checkpoint-"):
                    raise ValueError("Invalid checkpoint path")
                self.store = TinyVec.load(folder)
                if self.store.spec != spec:
                    raise ValueError("Checkpoint schema differs")
                watermark = pointer["sequence"]
            self.wal = WriteAheadLog(self.root / "mutations.jsonl")
            entries = self.wal.replay()
            if not 0 <= watermark <= self.wal.sequence:
                raise ValueError("Checkpoint is ahead of retained WAL")
            for entry in entries:
                if entry["sequence"] > watermark:
                    self._apply(entry["operation"], entry["data"])
        except BaseException:
            self.owner.close()
            raise

    def _ready(self):
        if self.closed:
            raise ValueError("Store is closed")

    def _apply(self, operation, data):
        if operation == "upsert":
            self.store.upsert(
                [
                    Record(
                        r["id"], np.array(r["vector"], dtype=np.float32), r["metadata"], r["text"]
                    )
                    for r in data
                ]
            )
        elif operation == "delete":
            self.store.delete(data)
        else:
            raise ValueError("Unknown WAL operation")

    def upsert(self, records):
        with self.lock:
            self._ready()
            checked = [checked_record(r, self.store.spec) for r in records]
            data = [{**asdict(r), "vector": r.vector.tolist()} for r in checked]
            sequence = self.wal.append("upsert", data)
            self._apply("upsert", data)
            return sequence

    def delete(self, ids):
        with self.lock:
            self._ready()
            ids = list(ids)
            if any(not isinstance(key, str) or not key for key in ids):
                raise ValueError("Expected nonempty string IDs")
            sequence = self.wal.append("delete", ids)
            self._apply("delete", ids)
            return sequence

    def search(self, *args, **kwargs):
        # Concurrent callers are safe, but the lazy exact index is protected by one lock.
        with self.lock:
            self._ready()
            return self.store.search(*args, **kwargs)

    def checkpoint(self):
        with self.lock:
            self._ready()
            name = "checkpoint-" + uuid.uuid4().hex
            self.store.save(self.root / name)
            pointer = {"directory": name, "sequence": self.wal.sequence}
            atomic_json(self.root / "checkpoint.json", pointer)
            # Retain the WAL: truncating it without an atomic generation protocol loses writes.
            return pointer

    def close(self):
        with self.lock:
            if not self.closed:
                self.store.close()
                self.owner.close()
                self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
