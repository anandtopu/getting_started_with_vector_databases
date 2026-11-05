"""Replace a listing atomically by its stable ID.

Run: uv run python modules/03_tinyvec/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/03_tinyvec/solutions/01_practice.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import copy


def solve(existing: dict, key: str, metadata: dict) -> dict:
    # KEY IDEA: this reference implements the stated acceptance policy.
    result = copy.deepcopy(existing)
    result[key] = copy.deepcopy(metadata)
    return result


def main() -> None:
    print(solve({"mug": {"price": 30}}, "mug", {"price": 20}))


if __name__ == "__main__":
    main()
