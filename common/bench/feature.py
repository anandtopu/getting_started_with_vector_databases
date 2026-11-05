"""Execute named Tier 2 lesson profiles and keep their observations outside retrieval rankings."""

import os
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

import yaml

from common.bench.config import load_config
from common.bench.hardware import hardware, provenance
from common.bench.runner import run_benchmark
from common.io import atomic_json
from common.settings import ROOT


def run_feature(path: Path, output: Path):
    profile = yaml.safe_load(path.read_text())
    folder = (ROOT / "modules" / profile["lesson"]).resolve()
    if folder.parent not in {(ROOT / "modules").resolve(), (ROOT / "modules/bonus").resolve()}:
        raise ValueError("Invalid lesson directory")
    observations = []
    for role in ("example", "native"):
        script = (folder / profile[role]).resolve()
        if not script.is_relative_to(folder) or script.suffix != ".py":
            raise ValueError("Expected a local lesson script")
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        if result.returncode:
            raise RuntimeError(f"{script.name} failed: {result.stderr[-3000:]}")
        observations.append(
            {
                "role": role,
                "script": script.relative_to(ROOT).as_posix(),
                "command": [sys.executable, str(script)],
                "total_script_seconds": time.perf_counter() - start,
                "stdout": result.stdout,
            }
        )
    report = {
        "profile": profile,
        "created_at": datetime.now(UTC).isoformat(),
        "hardware": hardware(),
        "provenance": provenance(),
        "observations": observations,
        "timing_scope": "Wall time for whole script including Python startup, setup, build, assertions and reporting. Retrieval timings are in the linked benchmark.",
    }
    if "retrieval_config" in profile:
        base = load_config(path.parent / profile["retrieval_config"])
        run = run_benchmark(base, output)
        report["retrieval_run"] = run["run_id"]
    result_path = output / "features" / f"{profile['feature']}-{uuid.uuid4().hex[:8]}.json"
    atomic_json(result_path, report)
    return result_path
