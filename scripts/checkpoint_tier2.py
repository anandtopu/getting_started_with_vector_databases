"""Tune on development queries and evaluate one frozen choice per family on held-out queries.
Run: uv run --extra libs --extra hnswlib python scripts/checkpoint_tier2.py
CPU: several minutes. Uses the local benchmark harness and optional native libraries. No Docker.
"""

import argparse
import importlib.util
import uuid
from pathlib import Path

import yaml

from common.bench.config import load_config
from common.bench.leaderboard import write_leaderboard
from common.bench.plots import write_plots
from common.bench.runner import run_benchmark
from common.bench.sweep import expand_sweep
from common.io import atomic_json
from common.settings import ROOT

TARGETS = {"lsh": 0.60, "ivf": 0.85, "hnsw": 0.90, "pq": 0.80}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    parser.add_argument(
        "--family", action="append", help="Run only named configs; repeat for several"
    )
    args = parser.parse_args()
    directory = ROOT / "configs/bench/tier2"
    decisions = []
    for path in sorted(directory.glob("*.yaml")):
        if args.family and path.stem not in args.family:
            continue
        if path.stem == "hnswlib" and importlib.util.find_spec("hnswlib") is None:
            print("SKIP hnswlib: install --extra hnswlib", flush=True)
            continue
        base = load_config(path)
        sweep = directory / "sweeps" / path.name
        configs = (
            expand_sweep(base, yaml.safe_load(sweep.read_text())) if sweep.exists() else [base]
        )

        def run(config):
            report = run_benchmark(config, args.output)
            print(report["run_id"], round(report["summary"]["recall_at_k"], 3), flush=True)
            return report

        runs = [run(cfg) for cfg in configs]
        floor = TARGETS.get(path.stem, 0.90)
        passing = [r for r in runs if r["summary"]["recall_at_k"] >= floor]
        winner = (
            max(passing, key=lambda r: r["summary"]["qps"])
            if passing
            else max(runs, key=lambda r: r["summary"]["recall_at_k"])
        )
        config = base.model_copy(
            update={
                "parameters": winner["config"]["parameters"],
                "name": base.name + "-test",
                "split": "test",
            }
        )
        held = run(config)
        row = {
            "family": path.stem,
            "target": floor,
            "development": [r["run_id"] for r in runs],
            "selected": winner["run_id"],
            "test": held["run_id"],
            "recall": held["summary"]["recall_at_k"],
            "target_met": held["summary"]["recall_at_k"] >= floor,
        }
        if path.stem in TARGETS:
            fixture_dev = [
                run(c.model_copy(update={"name": c.name + "-fixture-dev", "dataset": "fixture"}))
                for c in configs
            ]
            feasible = [r for r in fixture_dev if r["summary"]["recall_at_k"] >= floor]
            choice = (
                max(feasible, key=lambda r: r["summary"]["qps"])
                if feasible
                else max(fixture_dev, key=lambda r: r["summary"]["recall_at_k"])
            )
            fixture = run(
                config.model_copy(
                    update={
                        "name": base.name + "-fixture-test",
                        "dataset": "fixture",
                        "parameters": choice["config"]["parameters"],
                    }
                )
            )
            row.update(
                fixture_development=[r["run_id"] for r in fixture_dev],
                fixture_selection=choice["run_id"],
                fixture=fixture["run_id"],
                fixture_recall=fixture["summary"]["recall_at_k"],
                fixture_target_met=fixture["summary"]["recall_at_k"] >= floor,
            )
        decisions.append(row)
    atomic_json(args.output / "tier2" / f"decisions-{uuid.uuid4().hex[:8]}.json", decisions)
    write_leaderboard(args.output)
    write_plots(args.output)


if __name__ == "__main__":
    main()
