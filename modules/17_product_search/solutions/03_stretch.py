"""Stretch: protect identifiers after reranking.

Move an exact case-insensitive SKU match to the front without changing other ranks. Do not insert ineligible IDs.
Run: uv run python modules/17_product_search/solutions/03_stretch.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(ranked, sku_by_id, query):
    # KEY IDEA: Move an exact case-insensitive SKU match to the front without changing other ranks.
    literal = query.strip().casefold()
    return sorted(ranked, key=lambda key: sku_by_id.get(key, "").casefold() != literal)


def main() -> None:
    print(solve(*[["a", "b", "c"], {"a": "AA", "b": "BB", "c": "CC"}, " bb "]))


if __name__ == "__main__":
    main()
