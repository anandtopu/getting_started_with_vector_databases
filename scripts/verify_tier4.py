"""Run each new application example and publish exact execution evidence.
Run: uv run --extra qdrant --extra models --extra rag python scripts/verify_tier4.py --ollama
Omit --ollama to report local generation as skipped. Never downloads models.
"""

import argparse
import os
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from importlib.util import find_spec

import yaml

from common.bench.hardware import hardware, provenance
from common.bench.leaderboard import write_leaderboard
from common.io import atomic_json
from common.lesson_runtime import PACKAGES, requirements
from common.settings import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ollama", action="store_true")
    args = parser.parse_args()
    observations = {}
    for module in sorted((ROOT / "modules").glob("[12][0-9]_*")):
        if not 17 <= int(module.name[:2]) <= 20:
            continue
        for folder in ["examples", "use_case"]:
            for path in sorted((module / folder).glob("*.py")):
                extras, profile = requirements(path.read_text(encoding="utf8"))
                key = path.relative_to(ROOT).as_posix()
                if any(find_spec(PACKAGES[e]) is None for e in extras) or (
                    profile == "ollama" and not args.ollama
                ):
                    observations[key] = {"status": "skipped", "extras": extras, "profile": profile}
                    continue
                start = time.perf_counter()
                proc = subprocess.run(
                    [sys.executable, str(path)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf8",
                    errors="replace",
                    timeout=300,
                    env={**os.environ, "PYTHONUTF8": "1"},
                )
                observations[key] = {
                    "status": "passed" if proc.returncode == 0 else "failed",
                    "script": key,
                    "command": [sys.executable, key],
                    "total_script_seconds": time.perf_counter() - start,
                    "stdout": proc.stdout,
                    "error": proc.stderr[-3000:] if proc.returncode else "",
                }
                print(observations[key]["status"], key, flush=True)
    stamp = datetime.now(UTC).isoformat()
    machine, source = hardware(), provenance()
    atomic_json(
        ROOT / "results/tier4" / f"execution-{uuid.uuid4().hex[:8]}.json",
        {"created_at": stamp, "hardware": machine, "provenance": source, "scripts": observations},
    )
    for path in (ROOT / "configs/bench").glob("*.yaml"):
        config = yaml.safe_load(path.read_text())
        if not 17 <= int(config.get("lesson", "00")[:2]) <= 20:
            continue
        runs = []
        for role in ["example", "native"]:
            key = f"modules/{config['lesson']}/{config[role]}"
            result = observations[key]
            if result["status"] == "passed":
                runs.append({"role": role, **result})
        if len(runs) == 2:
            atomic_json(
                ROOT / "results/features" / f"{config['feature']}-{uuid.uuid4().hex[:8]}.json",
                {
                    "profile": config,
                    "created_at": stamp,
                    "hardware": machine,
                    "provenance": source,
                    "observations": runs,
                    "timing_scope": "Whole script diagnostic. Application quality and retrieval timings are in results/tier4.",
                },
            )
    write_leaderboard(ROOT / "results")
    if any(row["status"] == "failed" for row in observations.values()):
        raise SystemExit("Some examples failed. Inspect the saved execution report.")


if __name__ == "__main__":
    main()
