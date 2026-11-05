"""Practice: preserve strict price boundaries.

Return eligible IDs in input order. Under is strict, at most is inclusive. Missing prices are excluded.
Run: uv run python modules/17_product_search/solutions/01_practice.py
Expected: a runnable baseline or reference result. CPU: under one second.
Needs: base Python course environment. No models or services.
"""


def solve(rows, price, inclusive=False):
    # KEY IDEA: Return eligible IDs in input order.
    return [
        r["id"]
        for r in rows
        if "price" in r and (r["price"] <= price if inclusive else r["price"] < price)
    ]


def main() -> None:
    print(solve(*[[{"id": "a", "price": 10}, {"id": "b", "price": 11}], 10, False]))


if __name__ == "__main__":
    main()
