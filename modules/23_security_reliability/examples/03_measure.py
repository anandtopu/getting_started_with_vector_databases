"""Verify authenticated seller requests and persistent deletion in the real API.
Run: uv run python modules/23_security_reliability/examples/03_measure.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""
# course-extra: apps

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from common.apps.secure_api import create_app
from common.security.identity import Keyring, Principal


def main():
    token = "local-demo-admin-0123456789"
    ring = Keyring({token: Principal("admin", "seller-000", "admin")})
    headers = {"Authorization": "Bearer " + token}
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)

        def application():
            return create_app(keyring=ring, root=root, backend="tinyvec", limit=500)

        with TestClient(application()) as client:
            assert client.post("/search", json={}).status_code == 401
            rows = client.post("/search", json={}, headers=headers).json()["data"]["hits"]
            assert rows and all(r["metadata"]["seller_id"] == "seller-000" for r in rows)
            record_id = rows[0]["id"]
            assert client.post("/ops/backup", headers=headers).status_code == 200
            assert client.delete("/listings/" + record_id, headers=headers).status_code == 200
        with TestClient(application()) as client:
            rows = client.post("/search", json={}, headers=headers).json()["data"]["hits"]
            assert record_id not in [r["id"] for r in rows]
    print("No cross-tenant rows, unauthorized request rejected, deletion survives restart.")


if __name__ == "__main__":
    main()
