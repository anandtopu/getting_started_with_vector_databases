"""Measure every Tier 2 feature profile and update the results index.
Run: uv run --extra embedded --extra libs python scripts/run_tier2_features.py
CPU: several minutes. Uses included model artifacts and in-process libraries. No Docker.
"""

import argparse

import yaml

from common.bench.feature import run_feature
from common.bench.leaderboard import write_leaderboard
from common.bench.plots import write_plots
from common.settings import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature", action="append", help="Run a named profile; repeat as needed")
    selected = parser.parse_args().feature
    output = ROOT / "results"
    for path in sorted((ROOT / "configs/bench").glob("*.yaml")):
        profile = yaml.safe_load(path.read_text())
        if (
            "feature" in profile
            and 5 <= int(profile["lesson"][:2]) <= 10
            and (not selected or path.stem in selected)
        ):
            print(run_feature(path, output), flush=True)
    write_leaderboard(output)
    write_plots(output)


if __name__ == "__main__":
    main()
