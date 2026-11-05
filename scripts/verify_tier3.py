"""Run Tier 3 scripts once each and publish observations for profiles that ran.
Run: uv run --extra embedded --extra libs --extra apps python scripts/verify_tier3.py
Add --profiles pgvector,qdrant,... for services you started. The matched checkpoint runs must exist.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from importlib.util import find_spec
from pathlib import Path

import yaml

from common.bench.config import load_config
from common.bench.hardware import hardware, provenance
from common.bench.leaderboard import write_leaderboard
from common.bench.plots import write_plots
from common.io import atomic_json
from common.lesson_runtime import PACKAGES, requirements
from common.settings import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", default="")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    enabled = set(args.profiles.split(","))
    scripts = {}
    machine = hardware()
    source = provenance()
    for module in sorted((ROOT / "modules").glob("1[1-6]_*")):
        for sub in ("examples", "use_case"):
            for path in sorted((module / sub).glob("*.py")):
                text = path.read_text(encoding="utf8")
                extra, profile = requirements(text)
                key = path.relative_to(ROOT).as_posix()
                if (profile and profile not in enabled) or any(
                    find_spec(PACKAGES[x]) is None for x in extra
                ):
                    scripts[key] = {"status": "skipped", "extras": extra, "profile": profile}
                    continue
                start = time.perf_counter()
                command = [sys.executable, str(path)]
                proc = subprocess.run(
                    command,
                    cwd=ROOT,
                    timeout=300,
                    capture_output=True,
                    text=True,
                    encoding="utf8",
                    errors="replace",
                    env={**os.environ, "PYTHONUTF8": "1"},
                )
                scripts[key] = {
                    "status": "passed" if proc.returncode == 0 else "failed",
                    "command": command,
                    "total_script_seconds": time.perf_counter() - start,
                    "stdout": proc.stdout,
                    "error": proc.stderr[-2000:] if proc.returncode else "",
                }
                print(scripts[key]["status"], key, flush=True)
    stamp = datetime.now(UTC).isoformat()
    run_id = uuid.uuid4().hex[:8]
    validation = {
        "created_at": stamp,
        "hardware": machine,
        "provenance": source,
        "scripts": scripts,
    }
    atomic_json(args.output / "tier3" / f"execution-{run_id}.json", validation)
    for path in (ROOT / "configs/bench").glob("*.yaml"):
        cfg = yaml.safe_load(path.read_text())
        if not 11 <= int(cfg.get("lesson", "00")[:2]) <= 16:
            continue
        observations = []
        for role in ["example", "native"]:
            key = f"modules/{cfg['lesson']}/{cfg[role]}"
            if scripts.get(key, {}).get("status") != "passed":
                break
            observations.append({"role": role, "script": key, **scripts[key]})
        if len(observations) != 2:
            continue
        report = {
            "created_at": stamp,
            "profile": cfg,
            "hardware": machine,
            "provenance": source,
            "observations": observations,
            "execution_record": f"tier3/execution-{run_id}.json",
            "timing_scope": "Whole-script time includes interpreter startup, setup, native requests and teardown.",
        }
        if ref := cfg.get("retrieval_config"):
            name = load_config(path.parent / ref).name
            candidates = [
                json.loads(p.read_text(encoding="utf8"))
                for p in (args.output / "runs").glob(name + "-*.json")
            ]
            matching = [r for r in candidates if r["config"]["name"] == name]
            if matching:
                report["retrieval_run"] = max(matching, key=lambda r: r["created_at"])["run_id"]
        atomic_json(args.output / "features" / f"{cfg['feature']}-{run_id}.json", report)
    write_leaderboard(args.output)
    write_plots(args.output)
    failed = [key for key, row in scripts.items() if row["status"] == "failed"]
    if failed:
        raise SystemExit(f"Failed: {failed}")


if __name__ == "__main__":
    main()
