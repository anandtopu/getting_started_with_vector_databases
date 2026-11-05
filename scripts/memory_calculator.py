"""Compute transparent payload and capacity estimates.
Run: uv run python scripts/memory_calculator.py --rows 10000000 --dimensions 768
CPU: under a second; no data, network or services.
"""

import argparse
import json

from common.ops.capacity import estimate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=10_000_000)
    parser.add_argument("--dimensions", type=int, default=768)
    parser.add_argument("--replicas", type=int, default=2)
    parser.add_argument("--width", type=int, default=4)
    args = parser.parse_args()
    print(
        json.dumps(
            estimate(
                args.rows, args.dimensions, replicas=args.replicas, bytes_per_value=args.width
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
