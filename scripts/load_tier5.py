"""Run real Locust against an owned TLS API, including process failure and restart.
Run: uv run --extra apps python scripts/load_tier5.py
CPU: about two minutes; loopback only. No containers or model downloads.
"""

import csv
import json
import os
import ssl
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime

import httpx

from common.bench.hardware import hardware, provenance
from common.io import atomic_json
from common.settings import ROOT, cache_dir


def main():
    runtime = cache_dir() / "tier5/runtime"
    context = ssl.create_default_context(cafile=str(runtime / "tls/ca.pem"))
    output = ROOT / "results/tier5" / ("load-" + uuid.uuid4().hex[:8])
    output.mkdir(parents=True)
    environment = {**os.environ, "HF_HUB_OFFLINE": "1", "MARLOWE_APP_BACKEND": "tinyvec"}
    process = None
    worker = None
    rows = []
    with (output / "server.log").open("w") as log, httpx.Client(verify=context, timeout=2) as http:

        def start():
            child = subprocess.Popen(
                [sys.executable, "scripts/serve_tier5.py", "--port", "8444"],
                env=environment,
                stdout=log,
                stderr=log,
            )
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if child.poll() is not None:
                    raise RuntimeError("Owned API exited; inspect server.log")
                try:
                    if http.get("https://localhost:8444/health").status_code == 200:
                        return child
                except httpx.HTTPError:
                    pass
                time.sleep(0.2)
            child.terminate()
            child.wait(timeout=15)
            raise TimeoutError("TLS API readiness")

        try:
            process = start()
            for users, failure in [(1, False), (8, False), (32, False), (8, True)]:
                name = f"users-{users}" + ("-failure" if failure else "")
                prefix = output / name
                command = [
                    sys.executable,
                    "-m",
                    "locust",
                    "-f",
                    "load/locustfile.py",
                    "--headless",
                    "--host",
                    "https://localhost:8444",
                    "--users",
                    str(users),
                    "--spawn-rate",
                    str(users),
                    "--run-time",
                    "20s",
                    "--csv",
                    str(prefix),
                    "--csv-full-history",
                    "--only-summary",
                    "--exit-code-on-error",
                    "0",
                ]
                with (output / (name + ".log")).open("w") as load_log:
                    worker = subprocess.Popen(
                        command, env=environment, stdout=load_log, stderr=load_log
                    )
                    recovery = None
                    if failure:
                        time.sleep(7)
                        process.terminate()
                        process.wait(timeout=15)
                        started = time.perf_counter()
                        time.sleep(2)
                        process = start()
                        recovery = time.perf_counter() - started
                    worker.wait(timeout=50)
                    if worker.returncode:
                        raise RuntimeError("Locust failed to execute")
                with (output / (name + "_stats.csv")).open(newline="") as stream:
                    stats = list(csv.DictReader(stream))
                aggregate = next(row for row in stats if row["Name"] == "Aggregated")
                rows.append(
                    {
                        "users": users,
                        "failure_injected": failure,
                        "recovery_seconds": recovery,
                        "stats": aggregate,
                    }
                )
            admin = next(
                r
                for r in json.loads((runtime / "identities.json").read_text())
                if r["role"] == "admin"
            )
            metrics = http.get(
                "https://localhost:8444/metrics",
                headers={"Authorization": "Bearer " + admin["token"]},
                timeout=30,
            )
            metrics.raise_for_status()
            (output / "metrics.prom").write_text(metrics.text)
        finally:
            for child in [worker, process]:
                if child is not None and child.poll() is None:
                    child.terminate()
                    child.wait(timeout=15)
    atomic_json(
        output / "report.json",
        {
            "created_at": datetime.now(UTC).isoformat(),
            "hardware": hardware(),
            "provenance": provenance(),
            "command": "python scripts/load_tier5.py",
            "workload": "Two seller readers; frozen MiniLM queries; warm application cache; single API worker; 20-second runs; errors include admission 429 and injected downtime",
            "runs": rows,
        },
    )
    print(output)


if __name__ == "__main__":
    main()
