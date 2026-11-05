"""Evaluate native HNSW on a checksummed, licensed Fashion-MNIST subset.
Concepts: ground truth and evaluation.
Run: uv run python modules/bonus/B3_research_benchmarks/examples/02_production.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""
# course-extra: libs
# course-profile: public-benchmark

from common.research import public_benchmark, record


def main() -> None:
    result = public_benchmark()
    print({"efSearch": result["chosen_efSearch"], "heldout": result["heldout"]})
    print(
        record(
            "public-benchmark",
            result,
            "python modules/bonus/B3_research_benchmarks/examples/02_production.py",
        )
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
