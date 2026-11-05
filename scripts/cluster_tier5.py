"""Three real Qdrant peers, replica failure and recovery in an owned rootless pod.
Run: uv run --extra qdrant python scripts/cluster_tier5.py
CPU: minutes; requires rootless Podman and the pinned Qdrant image. Cleans its pod.
"""

import subprocess
import time
import uuid
from datetime import UTC, datetime

import httpx
import yaml

from common.bench.hardware import hardware, provenance
from common.io import atomic_json
from common.settings import ROOT


def main():
    engine = ["podman", "--connection", "podman-machine-default"]
    name = "marlowe-cluster-" + uuid.uuid4().hex[:8]
    image = yaml.safe_load((ROOT / "docker/compose.yaml").read_text())["services"]["qdrant"][
        "image"
    ]

    def run(*args):
        result = subprocess.run(
            [*engine, *args], check=True, capture_output=True, text=True, timeout=90
        )
        return result.stdout

    def wait(call, seconds=60):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                result = call()
                if result:
                    return result
            except (httpx.HTTPError, KeyError):
                pass
            time.sleep(0.3)
        raise TimeoutError("Cluster readiness")

    result = {
        "image": image,
        "nodes": 3,
        "shards": 2,
        "replicas": 3,
        "write_consistency_factor": 2,
        "network": "Loopback published REST; unencrypted internal lab-only pod network",
    }
    run(
        "pod",
        "create",
        "--name",
        name,
        "--label",
        "org.marlowe.course=phase7",
        "--network",
        "pasta",
        "-p",
        "127.0.0.1:6433:6333",
        "-p",
        "127.0.0.1:6436:6336",
        "-p",
        "127.0.0.1:6439:6339",
    )
    try:
        for i in range(3):
            port = 6333 + 3 * i
            command = [
                "run",
                "-d",
                "--pod",
                name,
                "--name",
                f"{name}-{i}",
                "--label",
                "org.marlowe.course=phase7",
                "-e",
                "QDRANT__CLUSTER__ENABLED=true",
                "-e",
                f"QDRANT__SERVICE__HTTP_PORT={port}",
                "-e",
                f"QDRANT__SERVICE__GRPC_PORT={port + 1}",
                "-e",
                f"QDRANT__CLUSTER__P2P__PORT={port + 2}",
                image,
                "./qdrant",
                "--uri",
                f"http://127.0.0.1:{port + 2}",
            ]
            if i:
                command += ["--bootstrap", "http://127.0.0.1:6335"]
            run(*command)
        with httpx.Client(base_url="http://127.0.0.1:6433", timeout=10) as http:
            wait(lambda: len(http.get("/cluster").json()["result"]["peers"]) == 3)
            response = http.put(
                "/collections/recovery",
                json={
                    "vectors": {"size": 2, "distance": "Cosine"},
                    "shard_number": 2,
                    "replication_factor": 3,
                    "write_consistency_factor": 2,
                },
            )
            response.raise_for_status()
            wait(lambda: http.get("/collections/recovery").json()["result"]["status"] == "green")

            def put(key):
                response = http.put(
                    "/collections/recovery/points?wait=true",
                    json={
                        "points": [{"id": key, "vector": [1.0, 0.0], "payload": {"tenant": "a"}}]
                    },
                )
                response.raise_for_status()
                return response.json()

            put(1)
            result["before"] = http.get("/collections/recovery/cluster").json()["result"]
            run("stop", "-t", "1", name + "-2")
            started = time.perf_counter()
            wait(lambda: put(2))
            result["write_with_one_peer_down_seconds"] = time.perf_counter() - started
            response = http.post(
                "/collections/recovery/points/query",
                params={"consistency": "majority"},
                json={"query": [1.0, 0.0], "limit": 10},
            )
            result["majority_read_status_during_failure"] = response.status_code
            if not response.is_success:
                result["majority_read_error"] = response.json().get("status")
                response = http.post(
                    "/collections/recovery/points/query",
                    params={"consistency": 1},
                    json={"query": [1.0, 0.0], "limit": 10},
                )
            response.raise_for_status()
            result["ids_during_failure"] = sorted(
                p["id"] for p in response.json()["result"]["points"]
            )
            result["failure_read_consistency"] = (
                "majority" if result["majority_read_status_during_failure"] == 200 else 1
            )
            assert result["ids_during_failure"] == [1, 2]
            started = time.perf_counter()
            run("start", name + "-2")
            with httpx.Client(base_url="http://127.0.0.1:6439", timeout=10) as recovered:

                def synchronized():
                    data = recovered.get("/collections/recovery/cluster").json()["result"]
                    local = data["local_shards"]
                    return (
                        len(local) == 2
                        and all(s["state"] == "Active" for s in local)
                        and sum(s["points_count"] for s in local) == 2
                    )

                wait(synchronized)
            result["rejoin_seconds"] = time.perf_counter() - started
            result["acknowledged_writes_lost"] = 0
            response = http.post(
                "/collections/recovery/points/query",
                params={"consistency": "majority"},
                json={"query": [1.0, 0.0], "limit": 10},
            )
            response.raise_for_status()
            result["majority_ids_after_recovery"] = sorted(
                p["id"] for p in response.json()["result"]["points"]
            )
            assert result["majority_ids_after_recovery"] == [1, 2]
            result["after"] = http.get("/collections/recovery/cluster").json()["result"]
    finally:
        # This UUID pod was created by this invocation; never target existing resources.
        run("pod", "rm", "-f", name)
    path = ROOT / "results/tier5" / ("cluster-" + uuid.uuid4().hex[:8] + ".json")
    atomic_json(
        path,
        {
            "created_at": datetime.now(UTC).isoformat(),
            "hardware": hardware(),
            "provenance": provenance(),
            "command": "python scripts/cluster_tier5.py",
            "observations": result,
            "cleanup": "Owned UUID pod removed",
        },
    )
    print(path)


if __name__ == "__main__":
    main()
