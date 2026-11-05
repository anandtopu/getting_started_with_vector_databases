"""Seller isolation, deletion and restart, with explicit native migration/load extensions.
Run: uv run --extra apps python capstones/04_multitenant_search/solution/project.py
Expected: two sellers isolated, foreign mutation denied, deleted listing stays absent.
CPU: seconds locally; --native adds TLS Qdrant and ~2-minute Locust verification.
"""

import argparse
import tempfile
from pathlib import Path

from common.apps.secure_market import SecureMarket
from common.errors import run_cli
from common.research import record
from common.security.identity import Principal


def scenario(root, backend="tinyvec"):
    alice = Principal("alice", "seller-000", "admin")
    bob = Principal("bob", "seller-001", "reader")
    market = SecureMarket(root, backend, limit=500)
    try:
        responses = {p.tenant: market.call(p, "search", {"query_id": "q000"}) for p in [alice, bob]}
        for tenant, response in responses.items():
            assert response["data"]["hits"] and all(
                h["metadata"]["seller_id"] == tenant for h in response["data"]["hits"]
            )
        first = responses[alice.tenant]["data"]["hits"][0]["id"]
        try:
            market.delete(bob, first)
        except PermissionError:
            pass
        else:
            raise AssertionError("Reader mutation accepted")
        market.backup(alice)
        deleted = market.delete(alice, first)
    finally:
        market.close()
    restored = SecureMarket(root, backend, limit=500)
    try:
        assert first not in [
            h["id"] for h in restored.call(alice, "search", {"query_id": "q000"})["data"]["hits"]
        ]
    finally:
        restored.close()
    return {
        "tenants": list(responses),
        "deleted": deleted,
        "isolation": True,
        "restart_deletion": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="tinyvec")
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        result = scenario(Path(temporary), args.backend)
    if args.native:
        from common.ops.native import native_migration_restore
        from scripts.load_tier5 import main as load

        result["migration"] = native_migration_restore()
        load()
    print(
        record(
            "capstone-tenants",
            result,
            "python capstones/04_multitenant_search/solution/project.py"
            + (" --native" if args.native else ""),
        )
    )


if __name__ == "__main__":
    run_cli(main)
