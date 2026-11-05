"""Runnable starting point for Capstone 04.
Run: uv run python capstones/04_multitenant_search/starter/project.py
Expected: a working baseline, not completed acceptance. CPU: seconds.
Needs: included vectors; no downloads, credentials or containers.
"""

from common.apps.database import AppDatabase
from common.apps.product_search import ProductSearch
from common.teaching import catalog


def main() -> None:
    with AppDatabase("tinyvec") as database:
        search = ProductSearch(database, limit=100)
        _, _, query, _ = catalog(100)
        # YOUR CODE HERE: add trusted identity, roles, branch scope and restore-safe deletion.
        print([h.id for h in search.search("mug", query).hits])
        print("Local baseline only: no authentication; do not deploy this starter.")


if __name__ == "__main__":
    main()
