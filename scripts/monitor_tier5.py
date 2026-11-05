"""Verify real Prometheus scraping and a provisioned Grafana dashboard in an owned pod.
Run: uv run --extra ops python scripts/monitor_tier5.py
CPU: about a minute; rootless Podman, pinned images and prepared TLS required.
"""

import json
import secrets
import ssl
import subprocess
import time
import uuid
from datetime import UTC, datetime

import httpx
import yaml

from common.bench.hardware import hardware, provenance
from common.io import atomic_json
from common.settings import ROOT, cache_dir


def main():
    runtime = cache_dir() / "tier5/runtime"
    folder = runtime / ("monitor-" + uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    keys = json.loads((runtime / "qdrant-keys.json").read_text())
    password = secrets.token_urlsafe(32)
    config = {
        "global": {"scrape_interval": "2s"},
        "scrape_configs": [
            {
                "job_name": "qdrant-secure",
                "scheme": "https",
                "static_configs": [{"targets": ["localhost:6333"]}],
                "authorization": {"credentials": keys["admin"]},
                "tls_config": {"ca_file": "/etc/prometheus/ca.pem", "server_name": "localhost"},
            }
        ],
    }
    (folder / "prometheus.yml").write_text(yaml.safe_dump(config))
    (folder / "prometheus.yml").chmod(0o600)
    (folder / "datasources.yml").write_text(
        yaml.safe_dump(
            {
                "apiVersion": 1,
                "datasources": [
                    {
                        "name": "Marlowe",
                        "type": "prometheus",
                        "uid": "marlowe",
                        "url": "http://localhost:9090",
                        "access": "proxy",
                        "isDefault": True,
                    }
                ],
            }
        )
    )
    (folder / "dashboards.yml").write_text(
        yaml.safe_dump(
            {
                "apiVersion": 1,
                "providers": [
                    {
                        "name": "Marlowe",
                        "type": "file",
                        "options": {"path": "/var/lib/grafana/dashboards"},
                    }
                ],
            }
        )
    )
    services = yaml.safe_load((ROOT / "docker/compose.yaml").read_text())["services"]
    engine = ["podman", "--connection", "podman-machine-default"]
    name = "marlowe-monitor-" + uuid.uuid4().hex[:8]

    def run(*args):
        return subprocess.run(
            [*engine, *args], check=True, capture_output=True, text=True, timeout=180
        ).stdout

    def wait(call):
        deadline = time.monotonic() + 75
        while time.monotonic() < deadline:
            try:
                value = call()
                if value:
                    return value
            except (httpx.HTTPError, KeyError, IndexError):
                pass
            time.sleep(0.5)
        raise TimeoutError("Monitoring readiness")

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
        "127.0.0.1:6533:6333",
        "-p",
        "127.0.0.1:9091:9090",
        "-p",
        "127.0.0.1:3001:3000",
    )
    try:
        qname, pname, gname = [name + s for s in ["-qdrant", "-prometheus", "-grafana"]]
        run(
            "create",
            "--pod",
            name,
            "--name",
            qname,
            "--label",
            "org.marlowe.course=phase7",
            "-e",
            "QDRANT__SERVICE__ENABLE_TLS=true",
            "-e",
            "QDRANT__TLS__CERT=/qdrant/server.pem",
            "-e",
            "QDRANT__TLS__KEY=/qdrant/server-key.pem",
            "-e",
            "QDRANT__SERVICE__API_KEY=" + keys["admin"],
            services["qdrant"]["image"],
        )
        for filename in ["server.pem", "server-key.pem"]:
            run("cp", str(runtime / "tls" / filename), qname + ":/qdrant/" + filename)
        run("start", qname)
        run(
            "create",
            "--pod",
            name,
            "--name",
            pname,
            "--label",
            "org.marlowe.course=phase7",
            services["prometheus"]["image"],
        )
        run("cp", str(folder / "prometheus.yml"), pname + ":/etc/prometheus/prometheus.yml")
        run("cp", str(runtime / "tls/ca.pem"), pname + ":/etc/prometheus/ca.pem")
        run("start", pname)
        run(
            "create",
            "--pod",
            name,
            "--name",
            gname,
            "--label",
            "org.marlowe.course=phase7",
            "-e",
            "GF_SECURITY_ADMIN_PASSWORD=" + password,
            "-e",
            "GF_ANALYTICS_REPORTING_ENABLED=false",
            services["grafana"]["image"],
        )
        run(
            "cp",
            str(folder / "datasources.yml"),
            gname + ":/etc/grafana/provisioning/datasources/marlowe.yml",
        )
        run(
            "cp",
            str(folder / "dashboards.yml"),
            gname + ":/etc/grafana/provisioning/dashboards/marlowe.yml",
        )
        run("cp", str(ROOT / "docker/grafana/dashboards"), gname + ":/var/lib/grafana/dashboards")
        run("start", gname)
        with httpx.Client(timeout=5) as http:
            wait(lambda: http.get("http://localhost:9091/-/ready").status_code == 200)
            up = wait(
                lambda: [
                    r
                    for r in http.get(
                        "http://localhost:9091/api/v1/query",
                        params={"query": "up{job='qdrant-secure'}"},
                    ).json()["data"]["result"]
                    if r["value"][1] == "1"
                ]
            )
            wait(
                lambda: http.get("http://localhost:3001/api/health").json().get("database") == "ok"
            )
            dashboard = wait(
                lambda: (
                    http.get(
                        "http://localhost:3001/api/dashboards/uid/marlowe-operations",
                        auth=("admin", password),
                    )
                    .json()
                    .get("dashboard")
                )
            )
            query = http.get(
                "http://localhost:9091/api/v1/query",
                params={"query": "count({job='qdrant-secure'})"},
            ).json()["data"]["result"]
            # Validate the CA and HTTP auth directly as well as through Prometheus.
            with httpx.Client(
                verify=ssl.create_default_context(cafile=str(runtime / "tls/ca.pem"))
            ) as secure:
                response = secure.get(
                    "https://localhost:6533/metrics", headers={"api-key": keys["admin"]}
                )
                response.raise_for_status()
            observations = {
                "up": up,
                "time_series": query,
                "dashboard_uid": dashboard["uid"],
                "panels": len(dashboard["panels"]),
                "images": {k: services[k]["image"] for k in ["qdrant", "prometheus", "grafana"]},
                "scope": "Live TLS Qdrant scrape and Grafana provisioning. API metrics separately captured by load test; cross-VM live API scrape not claimed.",
            }
    finally:
        run("pod", "rm", "-f", name)
    path = ROOT / "results/tier5" / ("monitoring-" + uuid.uuid4().hex[:8] + ".json")
    atomic_json(
        path,
        {
            "created_at": datetime.now(UTC).isoformat(),
            "hardware": hardware(),
            "provenance": provenance(),
            "observations": observations,
            "cleanup": "Owned UUID pod removed",
        },
    )
    print(path)


if __name__ == "__main__":
    main()
