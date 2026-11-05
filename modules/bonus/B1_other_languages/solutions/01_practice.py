"""Validate an explicit vector: return true only for the declared positive dimension, finite numbers and nonzero norm.
Run: uv run python modules/bonus/B1_other_languages/solutions/01_practice.py
Expected: a contract result; starters return None. CPU: under a second.
Needs: Python only; no models, data or services.
"""

import math


def solve(dimensions, vector):
    return (
        dimensions > 0
        and len(vector) == dimensions
        and all(math.isfinite(v) for v in vector)
        and any(v != 0 for v in vector)
    )


def main() -> None:
    print(solve(*[2, [1, 0]]))


if __name__ == "__main__":
    main()
