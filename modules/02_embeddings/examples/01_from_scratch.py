"""Project real catalog embeddings with a small PCA calculation.

Concepts: centering, SVD projection, lost information.
Run: uv run python modules/02_embeddings/examples/01_from_scratch.py
Expected: 500 x 2 coordinates; PCA distance agreement
CPU: about 2–10 seconds. Data: included Marlowe vectors or explicit hand features.
Models: no download; optional --live loads cached MiniLM where documented. Docker: none.
"""

import numpy as np
from sklearn.decomposition import PCA
from threadpoolctl import threadpool_limits

from common.settings import cache_dir
from common.teaching import catalog, evidence


def main() -> None:
    products, vectors, _, _ = catalog(500)
    centered = vectors - vectors.mean(axis=0)
    with threadpool_limits(limits=1):
        # KEY IDEA: the first two singular directions explain the most variance, not necessarily relevance.
        _, singular, directions = np.linalg.svd(centered, full_matrices=False)
        projected = centered @ directions[:2].T
        library = PCA(n_components=2, svd_solver="full").fit_transform(vectors)
    ours = np.linalg.norm(projected[1:] - projected[0], axis=1)
    theirs = np.linalg.norm(library[1:] - library[0], axis=1)
    np.testing.assert_allclose(ours, theirs, atol=1e-4)
    retained = float((singular[:2] ** 2).sum() / (singular**2).sum())
    evidence(
        "catalog_map",
        {
            "rows": len(products),
            "original_dimensions": vectors.shape[1],
            "projected_dimensions": 2,
            "variance_fraction": retained,
        },
    )
    print(projected.shape, "variance retained:", round(retained, 4))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
    for category in sorted(products["category"].unique()):
        mask = products["category"] == category
        ax.scatter(projected[mask, 0], projected[mask, 1], s=12, alpha=0.6, label=category)
    ax.set(
        xlabel="Principal component 1",
        ylabel="Principal component 2",
        title=f"Marlowe catalog: 2 of 384 dimensions; {retained:.1%} variance retained",
    )
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1, 1))
    path = cache_dir() / "tier1" / "catalog_map.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(path)
    print("Open the Playground Catalog map tab; search still uses all 384 coordinates.")


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
