"""Check that both hybrid branches respect a seller restriction.

Run: uv run --extra qdrant python modules/13_qdrant/use_case/seller_isolation.py
Concepts: Check that both hybrid branches respect a seller restriction.
Expected: the eligible product IDs or recovery decision shown in the README.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the qdrant profile first.
"""

# course-extra: qdrant
# course-profile: qdrant
from common.tier3 import observe, session


def main() -> None:
    # KEY IDEA: Check that both hybrid branches respect a seller restriction.
    with session("qdrant", 300) as (s, rows, q):
        seller = rows.iloc[0].seller_id
        expr = {"op": "eq", "field": "seller_id", "value": seller}
        found = s.hybrid_search(str(rows.iloc[1].sku), q, 5, expr)
        assert found and all(h.metadata["seller_id"] == seller for h in found)
        observe("qdrant-seller-scope", {"seller": seller, "returned": [h.id for h in found]})


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "qdrant")
