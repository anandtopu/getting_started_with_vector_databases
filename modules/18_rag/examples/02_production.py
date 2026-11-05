"""Index real help-center embeddings and retrieve scoped passages in Qdrant.

Run: uv run --extra qdrant python modules/18_rag/examples/02_production.py
Expected: buyer/north policy passages with stable source IDs.
CPU: seconds to one minute. Needs: qdrant extra, prepared RAG vectors. No implicit downloads.
"""
# course-extra: qdrant

import time

from common.apps.database import AppDatabase
from common.pretty import show_hits
from common.tier4 import open_rag


def main() -> None:
    with AppDatabase("qdrant-local") as db:
        rag, questions, queries = open_rag(db)
        q = questions[0]
        start = time.perf_counter()
        # KEY IDEA: role and region are eligibility, not hints to the generator.
        hits = rag.retrieve(q["question"], queries[q["id"]])
        show_hits(hits, (time.perf_counter() - start) * 1000, title="Retrieved policy evidence")
        print([h.metadata["passage_id"] for h in hits])
        assert all(h.metadata["role"] == "buyer" and h.metadata["region"] == "north" for h in hits)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
