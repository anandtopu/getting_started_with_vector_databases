"""Measure a controlled database comparison on the same catalog.

Run: uv run --extra embedded python modules/16_landscape/examples/03_measure.py
Concepts: Measure a controlled database comparison on the same catalog.
Expected: two matched embedded databases.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
from common.tier3 import measure


def main() -> None:
    # KEY IDEA: Measure a controlled database comparison on the same catalog.
    for backend in ("duckdb", "sqlite-vec"):
        result = measure(backend)
        print(backend, result["summary"]["qps"], result["hardware_id"])


if __name__ == "__main__":
    main()
