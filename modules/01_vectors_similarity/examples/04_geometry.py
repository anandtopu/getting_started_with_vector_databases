"""Draw hand-designed 2D and 3D product coordinates before using formulas.

Concepts: a vector as a point/arrow, units, third coordinate, projection.
Run: uv run python modules/01_vectors_similarity/examples/04_geometry.py
Expected: geometry.png with labeled 2D/3D product positions under the course cache.
CPU: about 2 seconds; tiny hand features, no downloads, models, or Docker.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common.settings import cache_dir
from common.teaching import hand_features


def main() -> None:
    ids, vectors, query = hand_features()
    # KEY IDEA: a third coordinate adds information that a 2D projection can hide.
    three = np.column_stack([vectors, [0.2, 0.1, 1.0, 0.4]])
    fig = plt.figure(figsize=(10, 4), layout="constrained")
    left = fig.add_subplot(121)
    right = fig.add_subplot(122, projection="3d")
    for key, point, point3 in zip(ids, vectors, three, strict=True):
        left.annotate(key, point, xytext=(4, 5), textcoords="offset points", fontsize=8)
        left.scatter(*point)
        right.scatter(*point3, label=key)
    left.arrow(0, 0, *query, width=0.006, color="black", length_includes_head=True)
    left.set(
        xlabel="Warmth (designed score)",
        ylabel="Portability (designed score)",
        xlim=(-0.1, 1.4),
        ylim=(-0.1, 1.2),
        title="Two coordinates and the query arrow",
    )
    right.set(
        xlabel="Warmth",
        ylabel="Portability",
        zlabel="Desk footprint",
        title="A third coordinate changes distance",
    )
    right.legend(fontsize=7)
    path = cache_dir() / "tier1" / "geometry.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)


if __name__ == "__main__":
    main()
