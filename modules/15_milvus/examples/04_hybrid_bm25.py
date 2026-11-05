"""Fuse a Milvus BM25 function and dense vector search.

Run: uv run --extra milvus python modules/15_milvus/examples/04_hybrid_bm25.py
Concepts: Fuse a Milvus BM25 function and dense vector search.
Expected: BM25 and dense RRF.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the milvus profile first.
"""

# course-extra: milvus
# course-profile: milvus
from common.tier3 import session


def main() -> None:
    # KEY IDEA: Fuse a Milvus BM25 function and dense vector search.
    with session("milvus", 160) as (s, rows, q):
        text = rows.iloc[0].sku
        bm25 = s.db.search(
            s.name,
            data=[text],
            anns_field="terms",
            limit=5,
            search_params={"metric_type": "BM25", "params": {}},
        )
        fused = s.hybrid_search(text, q, 5)
        assert bm25[0] and fused
        print("BM25", [(r["key"], r["distance"]) for r in bm25[0]], "RRF", [h.id for h in fused])


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "milvus")
