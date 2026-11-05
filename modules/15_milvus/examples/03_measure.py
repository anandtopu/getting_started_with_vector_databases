"""Measure a controlled database comparison on the same catalog.

Run: uv run --extra milvus python modules/15_milvus/examples/03_measure.py
Concepts: Measure a controlled database comparison on the same catalog.
Expected: three index families.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the milvus profile first.
"""

# course-extra: milvus
# course-profile: milvus
from common.tier3 import measure


def main() -> None:
    # KEY IDEA: Measure a controlled database comparison on the same catalog.
    for kind in ("FLAT", "HNSW", "IVF_FLAT"):
        measure("milvus", parameters={"index": kind})


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "milvus")
