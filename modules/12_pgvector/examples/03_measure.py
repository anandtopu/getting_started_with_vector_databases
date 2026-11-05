"""Measure a controlled database comparison on the same catalog.

Run: uv run --extra pgvector python modules/12_pgvector/examples/03_measure.py
Concepts: Measure a controlled database comparison on the same catalog.
Expected: flat / HNSW / IVFFlat timings.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the pgvector profile first.
"""

# course-extra: pgvector
# course-profile: pgvector
from common.tier3 import measure


def main() -> None:
    # KEY IDEA: Measure a controlled database comparison on the same catalog.
    for kind in ("flat", "hnsw", "ivfflat"):
        measure("pgvector", parameters={"index": kind})


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "pgvector")
