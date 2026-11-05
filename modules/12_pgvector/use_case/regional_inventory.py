"""Enforce inventory and budget constraints before recommending a replacement.

Run: uv run --extra pgvector python modules/12_pgvector/use_case/regional_inventory.py
Concepts: Enforce inventory and budget constraints before recommending a replacement.
Expected: the eligible product IDs or recovery decision shown in the README.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the pgvector profile first.
"""

# course-extra: pgvector
# course-profile: pgvector
from common.tier3 import observe, session


def main() -> None:
    # KEY IDEA: Enforce inventory and budget constraints before recommending a replacement.
    with session("pgvector", 300) as (s, _, q):
        expr = {
            "op": "and",
            "clauses": [
                {"op": "eq", "field": "region", "value": "north"},
                {"op": "lt", "field": "price", "value": 35},
                {"op": "gt", "field": "stock", "value": 0},
            ],
        }
        hits = s.search(q, 5, expr)
        assert hits and all(
            h.metadata["price"] < 35 and h.metadata["stock"] > 0 and h.metadata["region"] == "north"
            for h in hits
        )
        observe("postgres-regional-inventory", [(h.id, h.metadata["price"]) for h in hits])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "pgvector")
