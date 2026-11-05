"""Compare hypothetical managed price units without opening an account.

Run: uv run python modules/16_landscape/examples/09_managed_cost.py
Concepts: Compare hypothetical managed price units without opening an account.
Expected: hypothetical cost floor.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""


def estimate(storage_gib, months, reads, writes, price):
    metered = (
        storage_gib * months * price["storage"] + reads * price["read"] + writes * price["write"]
    )
    return max(months * price["monthly_minimum"], metered)


def main() -> None:
    # KEY IDEA: Compare hypothetical managed price units without opening an account.
    fictional = {"storage": 0.2, "read": 0.00001, "write": 0.00003, "monthly_minimum": 5}
    small = estimate(1, 1, 100, 100, fictional)
    large = estimate(10, 1, 1_000_000, 100_000, fictional)
    print("Illustrative dollars, not vendor quotes:", small, large)
    assert small == 5 and large > small


if __name__ == "__main__":
    main()
