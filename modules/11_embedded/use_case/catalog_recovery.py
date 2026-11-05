"""Recover the same product search after deleting a listing.

Run: uv run --extra embedded python modules/11_embedded/use_case/catalog_recovery.py
Concepts: Recover the same product search after deleting a listing.
Expected: the eligible product IDs or recovery decision shown in the README.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

# course-extra: embedded
from common.tier3 import observe, restore_drill


def main() -> None:
    # KEY IDEA: Recover the same product search after deleting a listing.
    observe("embedded-restore", [restore_drill(b) for b in ("chroma", "lancedb", "duckdb")])


if __name__ == "__main__":
    main()
