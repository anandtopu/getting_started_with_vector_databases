"""Build typed payload postings for two fictional sellers.

Run: uv run python modules/13_qdrant/examples/01_from_scratch.py
Concepts: Build typed payload postings for two fictional sellers.
Expected: IDs matching both postings.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

from common.data import records_from_products
from common.stores.filters import parse_filter
from common.teaching import catalog
from tinyvec.filters import MetadataIndex


def main() -> None:
    # KEY IDEA: Build typed payload postings for two fictional sellers.
    rows, matrix, _, _ = catalog(160)
    records = records_from_products(rows, matrix)
    expr = parse_filter(
        {
            "op": "and",
            "clauses": [
                {"op": "eq", "field": "region", "value": "north"},
                {"op": "lt", "field": "price", "value": 35},
            ],
        }
    )
    eligible = MetadataIndex(records).eligible(expr)
    assert eligible == {
        i
        for i, r in enumerate(records)
        if r.metadata["region"] == "north" and r.metadata["price"] < 35
    }
    print("eligible IDs", [records[i].id for i in sorted(eligible)])


if __name__ == "__main__":
    main()
