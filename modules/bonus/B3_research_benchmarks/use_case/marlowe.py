"""Apply the bonus concept to Marlowe inventory and evaluation.
Run: uv run python modules/bonus/B3_research_benchmarks/use_case/marlowe.py
Expected: protected invariants and an explained result. CPU: seconds.
Needs: included data; B1 additionally requires the prepared Node toolchain.
"""

from common.ops.capacity import estimate


def main() -> None:
    print(estimate(rows=3000, dimensions=784, replicas=1, links=24))
    print(
        "Pixel-space ANN recall is not product-photo relevance. Use SigLIP evaluation separately."
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
