"""Check Python, memory, disk, Docker/Compose, local ports, Ollama, and cached models.

Run: uv run python scripts/check_env.py [--services]
No downloads or mutations. CPU: seconds. --services probes localhost only.
"""

import argparse
import json
import platform
import shutil
import socket
import subprocess
from pathlib import Path

import httpx
import psutil

from common.embeddings import TEXT_MODEL, TEXT_REVISION
from common.settings import ROOT, cache_dir, setting

PORTS = {
    "pgvector": 5432,
    "qdrant": 6333,
    "weaviate": 8080,
    "weaviate-grpc": 50051,
    "milvus": 19530,
    "elasticsearch": 9200,
    "redis": 6379,
    "mongodb": 27017,
    "vespa": 8081,
    "ollama": 11434,
    "prometheus": 9090,
    "grafana": 3000,
}


def command_status(command: list[str]) -> dict:
    if not shutil.which(command[0]):
        return {"available": False, "detail": f"{command[0]} not installed"}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=8)
        return {
            "available": result.returncode == 0,
            "detail": (result.stdout + result.stderr).strip()[:1600],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "detail": str(exc)}


def inspect_environment(services: bool = False) -> dict:
    report = {
        "python": platform.python_version(),
        "python_supported": platform.python_version_tuple()[:2] == ("3", "12"),
        "ram_gib": round(psutil.virtual_memory().total / 2**30, 2),
        "free_disk_gib": round(shutil.disk_usage(ROOT).free / 2**30, 2),
        "docker": command_status(["docker", "info", "--format", "{{.ServerVersion}}"]),
        "compose": command_status(["docker", "compose", "version"]),
        "text_model": {
            "id": TEXT_MODEL,
            "revision": TEXT_REVISION,
            "cached": (
                cache_dir()
                / "models"
                / ("models--" + TEXT_MODEL.replace("/", "--"))
                / "snapshots"
                / TEXT_REVISION
            ).exists(),
        },
        "frozen_vectors": (ROOT / "data/embeddings_10k.parquet").exists(),
    }
    if services:
        report["ports"] = {}
        for name, port in PORTS.items():
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    report["ports"][name] = (
                        "occupied/listening; verify this is the intended service"
                    )
            except OSError:
                report["ports"][name] = "free or not listening"
        try:
            response = httpx.get(
                setting("OLLAMA_URL", "http://127.0.0.1:11434") + "/api/tags", timeout=2
            )
            response.raise_for_status()
            report["ollama_models"] = response.json()
        except httpx.HTTPError:
            report["ollama_models"] = (
                "Local Ollama is not running; only the RAG lesson requires it."
            )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--services", action="store_true")
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = inspect_environment(args.services)
    print(json.dumps(report, indent=2))
    if args.json:
        from common.io import atomic_json

        atomic_json(args.json, report)
    print(
        "Tiers 1–2 need no Docker. For server lessons, start your Linux container engine and select its Docker context. An occupied port may belong to another application; do not stop it blindly."
    )
    if not report["python_supported"]:
        raise SystemExit("Use Python 3.12 for the verified foundation lock.")


if __name__ == "__main__":
    main()
