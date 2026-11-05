"""Checksummed, fsynced mutation log with incomplete-tail recovery and one writer process."""

import hashlib
import json
import os

from common.io import canonical_json


class ProcessLock:
    def __init__(self, path):
        self.stream = path.open("a+b")
        if path.stat().st_size == 0:
            self.stream.write(b"0")
            self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.stream.close()
            raise ValueError("Another writer owns this TinyVec directory") from exc

    def close(self):
        if not self.stream.closed:
            self.stream.close()


class WriteAheadLog:
    def __init__(self, path):
        self.path = path
        self.sequence = 0
        self.poisoned = False
        path.touch(exist_ok=True)

    def replay(self):
        entries = []
        with self.path.open("r+b") as stream:
            good_offset = 0
            while line := stream.readline():
                if not line.endswith(b"\n"):
                    # KEY IDEA: discard only an incomplete final frame, never corrupt full records.
                    stream.truncate(good_offset)
                    stream.flush()
                    os.fsync(stream.fileno())
                    break
                frame = json.loads(line)
                payload = frame["payload"]
                digest = hashlib.sha256(canonical_json(payload).encode()).hexdigest()
                if digest != frame["sha256"] or payload["sequence"] != len(entries) + 1:
                    raise ValueError(
                        "Corrupt WAL checksum or sequence; restore from a verified backup"
                    )
                entries.append(payload)
                good_offset = stream.tell()
        self.sequence = len(entries)
        return entries

    def append(self, operation, data):
        if self.poisoned:
            raise RuntimeError("WAL write failed; close and recover before retrying")
        payload = {"sequence": self.sequence + 1, "operation": operation, "data": data}
        digest = hashlib.sha256(canonical_json(payload).encode()).hexdigest()
        frame = canonical_json({"payload": payload, "sha256": digest}).encode() + b"\n"
        try:
            with self.path.open("ab") as stream:
                stream.write(frame)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError:
            self.poisoned = True
            raise
        self.sequence += 1
        return self.sequence
