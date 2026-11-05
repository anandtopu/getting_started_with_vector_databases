"""Apply this module to Marlowe seller inventory.
Run: uv run python modules/23_security_reliability/use_case/marlowe.py
CPU: seconds; frozen fixtures only, no model downloads or services.
"""

import tempfile
from pathlib import Path

from common.apps.secure_market import SecureMarket
from common.security.identity import Principal


def main():
    with tempfile.TemporaryDirectory() as temporary:
        market = SecureMarket(Path(temporary), limit=500)
        try:
            alice = Principal("alice", "seller-000", "admin")
            bob = Principal("bob", "seller-001", "reader")
            for principal in [alice, bob]:
                response = market.call(principal, "search", {"query_id": "q000"})
                assert all(
                    r["metadata"]["seller_id"] == principal.tenant for r in response["data"]["hits"]
                )
            first = market.call(alice, "search", {"query_id": "q000"})["data"]["hits"][0]["id"]
            market.backup(alice)
            print(market.delete(alice, first))
            assert first not in [
                r["id"] for r in market.call(alice, "search", {"query_id": "q000"})["data"]["hits"]
            ]
        finally:
            market.close()


if __name__ == "__main__":
    main()
