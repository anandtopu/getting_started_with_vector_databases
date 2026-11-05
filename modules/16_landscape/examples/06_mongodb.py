"""Atlas Local search-index readiness and exact vector retrieval.

Run: uv run --extra landscape python modules/16_landscape/examples/06_mongodb.py
Concepts: Atlas Local search-index readiness and exact vector retrieval.
Expected: Atlas Local queryable index.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the mongodb profile first.
"""

# course-extra: landscape
# course-profile: mongodb
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Atlas Local search-index readiness and exact vector retrieval.
    with session("mongodb", 80) as (s, _, q):
        indexes = list(s.table.list_search_indexes("vectors"))
        assert indexes[0]["queryable"]
        print("native search index", indexes[0]["status"])
        hits = s.search(q, 5, {"op": "eq", "field": "region", "value": "north"})
        assert hits and all(h.metadata["region"] == "north" for h in hits)
        print("vector hits", [h.id for h in hits])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "mongodb")
