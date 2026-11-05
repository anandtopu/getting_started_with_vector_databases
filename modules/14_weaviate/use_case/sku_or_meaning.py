"""Compare an exact SKU and a shopper phrase at multiple hybrid weights.

Run: uv run --extra weaviate python modules/14_weaviate/use_case/sku_or_meaning.py
Concepts: Compare an exact SKU and a shopper phrase at multiple hybrid weights.
Expected: the eligible product IDs or recovery decision shown in the README.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; start the weaviate profile first.
"""

# course-extra: weaviate
# course-profile: weaviate
from common.tier3 import observe, session


def main() -> None:
    # KEY IDEA: Compare an exact SKU and a shopper phrase at multiple hybrid weights.
    with session("weaviate", 160) as (s, rows, q):
        outputs = []
        for alpha in (0.0, 0.5, 1.0):
            s.alpha = alpha
            for text in (rows.iloc[0].sku, "mug warmer"):
                hits = s.hybrid_search(text, q, 5)
                outputs.append({"alpha": alpha, "text": text, "ids": [h.id for h in hits]})
        assert all(r["ids"] for r in outputs)
        observe("weaviate-sku-meaning", outputs)


if __name__ == "__main__":
    from common.lesson_runtime import run_server_lesson

    run_server_lesson(main, "weaviate")
