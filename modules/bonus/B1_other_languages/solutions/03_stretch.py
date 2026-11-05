"""Return sorted IDs from rows [id,seller] belonging to a nonempty trusted seller.
Run: uv run python modules/bonus/B1_other_languages/solutions/03_stretch.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(rows, seller):
    return sorted(key for key, owner in rows if seller and owner == seller)


def main() -> None:
    print(solve(*[[["a", "one"], ["b", "two"]], "one"]))


if __name__ == "__main__":
    main()
