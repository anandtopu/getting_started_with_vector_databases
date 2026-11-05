"""Tour the catalog and inspect literal phrase matching.

Concepts: IDs, rows, text search.
Run: uv run python modules/00_setup/examples/01_from_scratch.py
Expected: 1,000 rows; phrase matches: 0
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

from common.data import load_products, search_queries


def literal_ids(rows: list[dict], text: str) -> list[str]:
    # KEY IDEA: characters must match; this procedure has no representation of intent.
    return [row["id"] for row in rows if text.casefold() in row["description"].casefold()]


def main() -> None:
    products = load_products(limit=1000)
    query = search_queries()[0]["text"]
    print(products[["id", "title", "price", "region"]].head().to_string(index=False))
    print(
        f"Rows: {len(products):,}; phrase matches: {len(literal_ids(products.to_dict('records'), query))}"
    )
    print("The input is a need. A phrase matcher cannot infer a heated coaster.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
