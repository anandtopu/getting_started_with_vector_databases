"""Separate search intent from exact eligibility rules.

Run: uv run  python modules/17_product_search/examples/01_from_scratch.py
Expected: three typed clauses; ambiguous alternatives produce a warning.
CPU: seconds to one minute. Needs: base environment. No implicit downloads.
"""

from dataclasses import asdict

from common.search.query_parser import parse_query
from common.stores.filters import matches, parse_filter


def main() -> None:
    parsed = parse_query("mug warmer under $100, in stock, in the north region")
    print(asdict(parsed))
    # KEY IDEA: filter comparisons have boundaries that similarity cannot enforce.
    eligible = matches({"price": 99.99, "stock": 1, "region": "north"}, parse_filter(parsed.filter))
    boundary = matches({"price": 100, "stock": 1, "region": "north"}, parse_filter(parsed.filter))
    assert eligible and not boundary
    print(parse_query("mug under $20 or over $100").warnings)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
