"""Replace a listing atomically by its stable ID.

Run: uv run python modules/03_tinyvec/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/03_tinyvec/exercises/01_practice.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""

import copy


def solve(existing: dict, key: str, metadata: dict) -> dict:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    result = copy.deepcopy(existing)
    result.setdefault(key, copy.deepcopy(metadata))
    return result


def main() -> None:
    print(solve({"mug": {"price": 30}}, "mug", {"price": 20}))


if __name__ == "__main__":
    main()
