"""Measure a controlled database comparison on the same catalog.

Run: uv run --extra embedded python modules/11_embedded/examples/03_measure.py
Concepts: Measure a controlled database comparison on the same catalog.
Expected: reproducible local benchmark.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
from common.tier3 import measure


def main() -> None:
    # KEY IDEA: Measure a controlled database comparison on the same catalog.
    for backend in ("chroma", "lancedb"):
        run = measure(backend)
        print(backend, run["summary"]["p95_ms"])


if __name__ == "__main__":
    main()
