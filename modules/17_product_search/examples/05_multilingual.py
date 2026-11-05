"""Compare real Qwen and MiniLM embeddings on a matched 500-row corpus.

Run: uv run  python modules/17_product_search/examples/05_multilingual.py
Expected: separate held-out nDCG for each model.
CPU: seconds to one minute. Needs: prepared Qwen vectors, base. No implicit downloads.
"""

from common.apps.database import AppDatabase
from common.apps.evaluation import multilingual_evaluation
from common.teaching import evidence


def main() -> None:
    with AppDatabase() as db:
        # KEY IDEA: re-embed both documents and queries when changing model space.
        result = multilingual_evaluation(db)
    print(result["held_out"])
    evidence("multilingual", result, tier=4)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
