"""Verified-TLS tenant load. Launched by scripts/load_tier5.py, never logs tokens."""

import itertools
import json

from locust import HttpUser, between, task

from common.settings import cache_dir

runtime = cache_dir() / "tier5/runtime"
identities = itertools.cycle(
    [r for r in json.loads((runtime / "identities.json").read_text()) if r["role"] == "reader"]
)


class Seller(HttpUser):
    wait_time = between(0.005, 0.02)

    def on_start(self):
        self.identity = next(identities)
        self.client.verify = str(runtime / "tls/ca.pem")
        self.client.headers["Authorization"] = "Bearer " + self.identity["token"]
        self.sequence = 0

    @task(4)
    def search(self):
        # Repeated queries give a declared warm-cache workload, not inference throughput.
        self.sequence += 1
        saved = [0, 1, 2, 3, 4, 6, 7, 8, 9]
        with self.client.post(
            "/search",
            json={"query_id": f"q{saved[self.sequence % len(saved)]:03}", "k": 5},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                rows = response.json()["data"]["hits"]
                if any(row["metadata"]["seller_id"] != self.identity["tenant"] for row in rows):
                    response.failure("TENANT_ISOLATION_VIOLATION")
            # 429 remains a measured failed request, never silently counted as success.

    @task(1)
    def filtered_search(self):
        self.client.post(
            "/search",
            name="/search filtered",
            json={"query_id": "q000", "filter": {"op": "lt", "field": "price", "value": 100}},
        )
