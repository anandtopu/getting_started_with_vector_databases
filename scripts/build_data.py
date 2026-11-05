"""Generate seeded Marlowe products, judgments, policies, drawings, reviews and events.

Run: uv run python scripts/build_data.py
Expected: Generated 50,000 products and 2,000 drawings. CPU: about 1–3 minutes.
Needs: core environment, about 300 MB disk; no model, network, or Docker.
"""

import argparse

from common.errors import run_cli
from common.generation import SEED, build_data
from common.settings import data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--products", type=int, default=50_000)
    parser.add_argument("--images", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    build_data(data_dir(), args.products, args.images, args.seed)
    print(f"Generated {args.products:,} products and {args.images:,} drawings in {data_dir()}.")


if __name__ == "__main__":
    run_cli(main)
