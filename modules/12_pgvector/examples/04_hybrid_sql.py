"""Fuse Postgres text matches with dense neighbors.

Run: uv run --extra pgvector python modules/12_pgvector/examples/04_hybrid_sql.py
Concepts: Fuse Postgres text matches with dense neighbors.
Expected: ranked SKU hits.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the pgvector profile first.
"""

# course-extra: pgvector
# course-profile: pgvector
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Fuse Postgres text matches with dense neighbors.
    with session("pgvector") as (store, rows, q):
        sku = rows.iloc[0].sku
        hits = store.hybrid_search(sku, q, 10)
        print("SKU", sku, "fused", [(h.id, h.score) for h in hits])
        assert rows.iloc[0].id in [h.id for h in hits]


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "pgvector")
