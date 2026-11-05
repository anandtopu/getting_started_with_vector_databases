"""Allowlisted audit fields omit credentials, user text, vectors and private metadata."""

import json
import os
from datetime import UTC, datetime
from threading import Lock


class AuditLog:
    def __init__(self, path):
        self.path = path
        self.lock = Lock()

    def record(self, *, subject, tenant, action, outcome, request_id):
        row = {
            "time": datetime.now(UTC).isoformat(),
            "subject": subject,
            "tenant": tenant,
            "action": action,
            "outcome": outcome,
            "request_id": request_id,
        }
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf8") as stream:
                stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        return row
