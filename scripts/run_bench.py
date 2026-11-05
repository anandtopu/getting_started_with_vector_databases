"""Measure one config or a parameter sweep and regenerate the leaderboard/plots.

Run: uv run python scripts/run_bench.py configs/bench/exact_fixture.yaml
Expected: run ID, recall, QPS and results path. CPU: seconds to minutes.
Needs: core environment and fixture generation; catalog configs use committed vectors.
No model downloads. sqlite-vec config needs --extra embedded. No Docker.
"""

import argparse
from pathlib import Path

import yaml

from common.bench.config import load_config
from common.bench.leaderboard import write_leaderboard
from common.bench.plots import write_plots
from common.bench.runner import run_benchmark
from common.bench.sweep import expand_sweep
from common.errors import run_cli
from common.settings import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--sweep", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    if "feature" in yaml.safe_load(args.config.read_text()):
        from common.bench.feature import run_feature

        if args.sweep:
            parser.error("Use the retrieval config named in the feature profile for a sweep")
        print(run_feature(args.config, args.output))
        print(write_leaderboard(args.output))
        write_plots(args.output)
        return
    base = load_config(args.config)
    configs = (
        expand_sweep(base, yaml.safe_load(args.sweep.read_text(encoding="utf-8")))
        if args.sweep
        else [base]
    )
    for config in configs:
        run = run_benchmark(config, args.output)
        print(
            f"{run['run_id']}: recall={run['summary']['recall_at_k']}, QPS={run['summary']['qps']:.2f}"
        )
    print(write_leaderboard(args.output))
    for plot in write_plots(args.output):
        print(plot)


if __name__ == "__main__":
    run_cli(main)
