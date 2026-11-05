"""Elasticsearch HNSW and a keyword query.

Run: uv run --extra landscape python modules/16_landscape/examples/04_elasticsearch.py
Concepts: Elasticsearch HNSW and a keyword query.
Expected: Elasticsearch dense and text hits.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the elasticsearch profile first.
"""

# course-extra: landscape
# course-profile: elasticsearch
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Elasticsearch HNSW and a keyword query.
    with session("elasticsearch", 80) as (s, _, q):
        rows = s.db.search(
            index=s.name, query={"match": {"body": "mug warmer"}}, size=3, source=False
        )["hits"]["hits"]
        print("lexical IDs", [r["_id"] for r in rows])
        hits = s.search(q, 5, {"op": "eq", "field": "region", "value": "north"})
        assert hits and all(h.metadata["region"] == "north" for h in hits)
        print("vector hits", [h.id for h in hits])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "elasticsearch")
