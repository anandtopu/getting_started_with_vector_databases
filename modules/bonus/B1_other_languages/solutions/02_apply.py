"""Map business IDs to native IDs. Return a dictionary, rejecting duplicate business IDs or mismatched lengths.
Run: uv run python modules/bonus/B1_other_languages/solutions/02_apply.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""


def solve(ids, native_ids):
    if len(ids) != len(native_ids) or len(set(ids)) != len(ids):
        return None
    return dict(zip(ids, native_ids, strict=True))


def main() -> None:
    print(solve(*[["a", "b"], [1, 2]]))


if __name__ == "__main__":
    main()
