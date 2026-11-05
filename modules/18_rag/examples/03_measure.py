"""Measure how a narrow IVF probe and post-filtering lose RAG evidence.

Run: uv run  python modules/18_rag/examples/03_measure.py
Expected: exact and approximate passage recall over 80 questions.
CPU: seconds to one minute. Needs: base, frozen help vectors. No implicit downloads.
"""

from common.apps.database import AppDatabase
from common.apps.evaluation import rag_evaluation
from common.teaching import evidence


def main() -> None:
    with AppDatabase() as db:
        # KEY IDEA: assess source passage recall before asking the generator to answer.
        result = rag_evaluation(db)
    print({k: v for k, v in result.items() if k != "rows"})
    evidence("rag-index-quality", result, tier=4)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
