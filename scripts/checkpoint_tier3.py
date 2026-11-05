"""Run each selected real database on one frozen held-out workload.
Run: uv run --extra embedded python scripts/checkpoint_tier3.py
CPU: a few minutes, no model downloads. Add server backends only after starting profiles.
"""

import argparse
from pathlib import Path

from common.bench.config import load_config
from common.bench.leaderboard import write_leaderboard
from common.bench.plots import write_plots
from common.bench.runner import run_benchmark
from common.settings import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backends", nargs="+", default=["chroma", "lancedb", "sqlite-vec", "duckdb"]
    )
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    for backend in args.backends:
        path = ROOT / "configs/bench/tier3" / (backend + ".yaml")
        if path.parent != ROOT / "configs/bench/tier3" or not path.exists():
            parser.error(f"Unknown database {backend}")
        report = run_benchmark(load_config(path), args.output)
        print(report["run_id"], report["summary"]["recall_at_k"], flush=True)
    write_leaderboard(args.output)
    write_plots(args.output)


if __name__ == "__main__":
    main()
