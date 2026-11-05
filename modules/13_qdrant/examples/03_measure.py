"""Measure a controlled database comparison on the same catalog.

Run: uv run --extra qdrant python modules/13_qdrant/examples/03_measure.py
Concepts: Measure a controlled database comparison on the same catalog.
Expected: filtered and keyword query sweep.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the qdrant profile first.
"""

# course-extra: qdrant
# course-profile: qdrant
from common.tier3 import measure


def main() -> None:
    # KEY IDEA: Measure a controlled database comparison on the same catalog.
    for quantized in [False, True]:
        measure("qdrant", parameters={"quantize": quantized}, query_types=["filtered", "keyword"])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "qdrant")
