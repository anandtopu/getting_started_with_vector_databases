"""Vespa tensor ranking and structured document retrieval.

Run: uv run --extra landscape python modules/16_landscape/examples/07_vespa.py
Concepts: Vespa tensor ranking and structured document retrieval.
Expected: Vespa tensor score.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the vespa profile first.
"""

# course-extra: landscape
# course-profile: vespa
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Vespa tensor ranking and structured document retrieval.
    with session("vespa", 80) as (s, _, q):
        first = next(iter(s.catalog))
        result = s.db.get(s.path(first)).raise_for_status().json()
        print("native document", result["id"], "scope", result["fields"]["scope"])
        hits = s.search(q, 5, {"op": "eq", "field": "region", "value": "north"})
        assert hits and all(h.metadata["region"] == "north" for h in hits)
        print("vector hits", [h.id for h in hits])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "vespa")
