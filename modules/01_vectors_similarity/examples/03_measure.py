"""Observe distance concentration under a controlled distribution.

Concepts: random math experiment, distance spread, KDTree versus brute force.
Run: uv run python modules/01_vectors_similarity/examples/03_measure.py
Expected: relative spread generally shrinks; measured tree/brute times
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors
from threadpoolctl import threadpool_limits

from common.teaching import evidence, timed


def main() -> None:
    rng = np.random.default_rng(20261104)
    rows = []
    with threadpool_limits(limits=1):
        for dimensions in [2, 8, 32, 128, 512]:
            matrix = rng.normal(size=(1000, dimensions)).astype(np.float32)
            queries = rng.normal(size=(20, dimensions)).astype(np.float32)
            distances = np.linalg.norm(matrix - queries[0], axis=1)
            row = {
                "dimensions": dimensions,
                "coefficient_of_variation": float(distances.std() / distances.mean()),
            }
            for method in ["brute", "kd_tree"]:
                model = NearestNeighbors(algorithm=method, n_neighbors=5, n_jobs=1).fit(matrix)
                row[method] = timed(lambda model=model, queries=queries: model.kneighbors(queries))
            rows.append(row)
            print(
                dimensions,
                round(row["coefficient_of_variation"], 4),
                {m: round(row[m]["median_ms"], 3) for m in ["brute", "kd_tree"]},
            )
    # KEY IDEA: shrinking relative spread is distribution-dependent, not proof every real dataset is hopeless.
    assert rows[-1]["coefficient_of_variation"] < rows[0]["coefficient_of_variation"]
    evidence(
        "dimensions",
        {"distribution": "independent standard normal; math-only demonstration", "rows": rows},
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
