"""Send concurrent operations through the durable HTTP service and restart it.
Concepts: durability and replay.
Run: uv run python modules/bonus/B2_tinyvec_service/examples/03_measure.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""
# course-extra: apps

import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient

from common.research import record
from tinyvec.service import create_app


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        with TestClient(create_app(root)) as client:

            def send(i):
                response = client.post(
                    "/records", json={"records": [{"id": str(i), "vector": [1.0, i / 100]}]}
                )
                assert response.status_code == 200
                return response.json()["sequence"]

            with ThreadPoolExecutor(max_workers=4) as pool:
                sequences = list(pool.map(send, range(20)))
            assert sorted(sequences) == list(range(1, 21))
        with TestClient(create_app(root)) as client:
            recovered = client.get("/health").json()["sequence"]
            assert recovered == 20
        print(
            record(
                "durable-service",
                {
                    "concurrent_clients": 4,
                    "acknowledged": 20,
                    "recovered_sequence": recovered,
                    "scope": "Loopback test transport; serialized storage lock, no power-cut simulation",
                },
                "python modules/bonus/B2_tinyvec_service/examples/03_measure.py",
            )
        )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
