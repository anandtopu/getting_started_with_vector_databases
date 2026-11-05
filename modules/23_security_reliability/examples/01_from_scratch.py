"""Authenticate a trusted identity and demonstrate a hostile filter boundary.
Run: uv run python modules/23_security_reliability/examples/01_from_scratch.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""

import json
import tempfile
from pathlib import Path

from common.ops.tenancy import tenant_filter
from common.security.audit import AuditLog
from common.security.identity import Keyring, Principal


def main():
    principal = Principal("reader-a", "seller-a", "reader")
    token = "local-test-token-0123456789"
    keys = Keyring({token: principal})
    assert keys.authenticate(token) == principal
    assert principal.permits("read") and not principal.permits("write")
    hostile = {"op": "or", "conditions": [{"op": "eq", "field": "seller_id", "value": "seller-b"}]}
    print(tenant_filter(principal, hostile))
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "audit.jsonl"
        audit = AuditLog(path)
        audit.record(
            subject=principal.subject,
            tenant=principal.tenant,
            action="/search",
            outcome="200",
            request_id="demo",
        )
        event = json.loads(path.read_text())
        assert token not in path.read_text() and "query" not in event
        print(event)
    print("Audit records identity and outcome, never request bodies or embeddings.")


if __name__ == "__main__":
    main()
