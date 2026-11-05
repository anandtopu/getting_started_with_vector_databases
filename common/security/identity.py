"""Server-owned bearer-key identities. Request bodies never choose a tenant or role."""

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant: str
    role: str

    def permits(self, action):
        return self.role in {
            "read": {"reader", "writer", "admin"},
            "write": {"writer", "admin"},
            "admin": {"admin"},
        }.get(action, set())


class Keyring:
    def __init__(self, keys):
        if not keys:
            raise ValueError(
                "Configure at least one identity; there are no default deployment keys"
            )
        self.keys = []
        for token, principal in keys.items():
            if (
                len(token) < 16
                or principal.role not in {"reader", "writer", "admin"}
                or not principal.tenant
            ):
                raise ValueError("Invalid key or principal")
            self.keys.append((hashlib.sha256(token.encode()).digest(), principal))

    @classmethod
    def from_file(cls, path: Path):
        values = json.loads(path.read_text(encoding="utf8"))
        return cls(
            {row["token"]: Principal(row["subject"], row["tenant"], row["role"]) for row in values}
        )

    def authenticate(self, token):
        supplied = hashlib.sha256(token.encode()).digest()
        for expected, principal in self.keys:
            if hmac.compare_digest(supplied, expected):
                return principal
        raise PermissionError("Invalid credentials")
