"""Create local-only random identities and TLS material, never default passwords.
Run: uv run --extra ops python scripts/prepare_tier5.py
CPU: seconds. Secrets live only under the ignored course cache.
"""

import json
import secrets

from common.io import atomic_json
from common.security.tls import create_local_certificate
from common.settings import cache_dir


def main():
    root = cache_dir() / "tier5/runtime"
    root.mkdir(parents=True, exist_ok=True)
    root.chmod(0o700)
    if not (root / "identities.json").exists():
        identities = [
            {"subject": name, "tenant": tenant, "role": role, "token": secrets.token_urlsafe(32)}
            for name, tenant, role in [
                ("seller-a-reader", "seller-000", "reader"),
                ("seller-a-admin", "seller-000", "admin"),
                ("seller-b-reader", "seller-001", "reader"),
            ]
        ]
        atomic_json(root / "identities.json", identities)
        (root / "identities.json").chmod(0o600)
    if not (root / "qdrant-keys.json").exists():
        atomic_json(
            root / "qdrant-keys.json",
            {"admin": secrets.token_urlsafe(32), "read": secrets.token_urlsafe(32)},
        )
        (root / "qdrant-keys.json").chmod(0o600)
    if not (root / "tls/server.pem").exists():
        create_local_certificate(root / "tls")
    keys = json.loads((root / "qdrant-keys.json").read_text())
    if not (root / "compose.env").exists():
        (root / "compose.env").write_text(
            "MARLOWE_QDRANT_ADMIN="
            + keys["admin"]
            + "\nMARLOWE_QDRANT_READ="
            + keys["read"]
            + "\nMARLOWE_GRAFANA_PASSWORD="
            + secrets.token_urlsafe(32)
            + "\n"
        )
        (root / "compose.env").chmod(0o600)
    (root / "qdrant-metrics-token").write_text(keys["admin"])
    # The host directory is private; a single read-only bind lets non-root Prometheus read it.
    (root / "qdrant-metrics-token").chmod(0o644)
    admin = next(
        row for row in json.loads((root / "identities.json").read_text()) if row["role"] == "admin"
    )
    (root / "api-metrics-token").write_text(admin["token"])
    (root / "api-metrics-token").chmod(0o600)
    print(
        f"Prepared identities and local TLS under {root}. No secrets printed. Certificates expire after 30 days."
    )


if __name__ == "__main__":
    main()
