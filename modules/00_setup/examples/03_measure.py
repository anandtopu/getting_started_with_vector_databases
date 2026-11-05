"""Measure the motivating exact-search session.

Concepts: phrase baseline, useful hits, repeated timing.
Run: uv run python modules/00_setup/examples/03_measure.py
Expected: 0 literal matches; 5 mug warmers; evidence JSON
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.apps.search import open_catalog, search_saved
from common.pretty import show_hits
from common.teaching import evidence, timed


def main() -> None:
    store, products, _ = open_catalog(limit=1000)
    try:
        query, hits, elapsed = search_saved(store)
        literal = int(
            products["description"].str.contains(query["text"], case=False, regex=False).sum()
        )
        useful = sum("mug warmer" in hit.metadata["title"] for hit in hits)
        # KEY IDEA: a successful motivating query is evidence for this query, not a whole benchmark.
        assert literal == 0 and useful == 5
        show_hits(hits, elapsed, title="First useful search")
        evidence(
            "orientation",
            {
                "literal_matches": literal,
                "mug_warmers_at_5": useful,
                "saved_search_including_query_load": timed(lambda: search_saved(store)),
            },
        )
    finally:
        store.close()


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
