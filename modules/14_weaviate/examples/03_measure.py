"""Measure a controlled database comparison on the same catalog.

Run: uv run --extra weaviate python modules/14_weaviate/examples/03_measure.py
Concepts: Measure a controlled database comparison on the same catalog.
Expected: judged hybrid workloads.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the weaviate profile first.
"""

# course-extra: weaviate
# course-profile: weaviate
from common.tier3 import measure


def main() -> None:
    # KEY IDEA: Measure a controlled database comparison on the same catalog.
    for alpha in (0.0, 0.5, 1.0):
        measure(
            "weaviate",
            retrieval="hybrid",
            parameters={"alpha": alpha},
            query_types=["keyword", "semantic"],
        )


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "weaviate")
