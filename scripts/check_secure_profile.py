"""Wait for the explicitly started, authenticated TLS database.
Run: uv run --extra qdrant python scripts/check_secure_profile.py
CPU: at most about a minute; no implicit container startup.
"""

import time

from common.ops.native import client


def main():
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        try:
            with client() as db:
                db.get_collections()
            print("Authenticated TLS Qdrant is ready")
            return
        except Exception:
            time.sleep(0.5)
    raise TimeoutError("Secure Qdrant unavailable; check the Tier 5 setup and certificate")


if __name__ == "__main__":
    main()
