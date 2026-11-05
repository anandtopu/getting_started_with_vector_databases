"""Flagship evaluation joins all five app flows and operational recovery evidence.
Run: uv run --extra qdrant python capstones/05_marlowe_search/solution/project.py --backend qdrant-local
Expected: retrieval, RAG, recommendation/duplicate and photo reports; verified restore.
CPU: minutes. Frozen real-model artifacts; --operations adds explicit local service drills.
"""

import argparse

from common.apps.database import AppDatabase
from common.apps.evaluation import (
    photo_evaluation,
    rag_evaluation,
    recommendation_evaluation,
    search_evaluation,
)
from common.errors import run_cli
from common.ops.drills import disaster_recovery
from common.research import record


def evaluate(backend):
    observations = {"backend": backend}
    # Each evaluation owns a fresh session so stale collections cannot affect the next flow.
    for name, run in [
        ("search", search_evaluation),
        ("rag", rag_evaluation),
        ("recommendations_and_duplicates", recommendation_evaluation),
        ("photo", photo_evaluation),
    ]:
        with AppDatabase(backend) as database:
            observations[name] = run(database)
        print(f"Completed {name} evaluation with {backend}", flush=True)
    observations["restore"] = disaster_recovery()
    return observations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="tinyvec")
    parser.add_argument("--operations", action="store_true")
    args = parser.parse_args()
    result = evaluate(args.backend)
    if args.operations:
        from common.ops.native import native_migration_restore, native_security
        from scripts.monitor_tier5 import main as monitoring

        result["database_tls"] = native_security()
        result["native_restore"] = native_migration_restore()
        monitoring()
    print(
        record(
            "capstone-flagship",
            result,
            "python capstones/05_marlowe_search/solution/project.py --backend "
            + args.backend
            + (" --operations" if args.operations else ""),
        )
    )


if __name__ == "__main__":
    run_cli(main)
