"""Compute MMR from relevance minus similarity to already selected items.

Run: uv run  python modules/19_recommendations/examples/01_from_scratch.py
Expected: high diversity selects a different second item.
CPU: seconds to one minute. Needs: base, NumPy. No implicit downloads.
"""

import numpy as np

from common.apps.recommendations import mmr


def main() -> None:
    ids = ["red-mug", "red-mug-copy", "blue-travel-cup"]
    vectors = np.array([[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]])
    # KEY IDEA: selecting an item changes the redundancy penalty on the next iteration.
    for relevance in [1.0, 0.7, 0.2]:
        print(relevance, mmr(ids, vectors, [1, 0], k=2, relevance=relevance))
    assert mmr(ids, vectors, [1, 0], 2, 0.2)[1] == "blue-travel-cup"


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
