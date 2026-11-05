"""Compare literal keyword matching with genuine offline semantic retrieval.

Run: uv run python examples/01_quickstart.py
Expected: literal phrase matches: 0; semantic hits include ceramic mug warmers.
CPU: about 2 seconds. Needs: committed 10k products/query vectors and core packages.
No model download, Docker, or network. Scores/timings vary by hardware.
"""

from common.apps.search import open_catalog, search_saved
from common.errors import run_cli
from common.pretty import show_hits


def main() -> None:
    store, products, _ = open_catalog()
    try:
        query, hits, milliseconds = search_saved(store)
        literal = products["description"].str.contains(query["text"], case=False, regex=False)
        print(f"Query: {query['text']}")
        print(f"Literal phrase matches: {int(literal.sum())}")
        # KEY IDEA: the query and products were encoded by the same frozen real model.
        show_hits(hits, milliseconds)
    finally:
        store.close()


if __name__ == "__main__":
    run_cli(main)
