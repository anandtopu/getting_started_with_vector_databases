"""Plot actual bonus observations with distinct development and held-out markers.

Run: uv run python scripts/plot_bonus.py
CPU: seconds. Requires existing results/bonus records; no models or network.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.io import atomic_json
from common.settings import ROOT


def main() -> None:
    def latest(pattern, corrected=False):
        paths = sorted((ROOT / "results/bonus").glob(pattern), key=lambda p: p.stat().st_mtime)
        for path in reversed(paths):
            report = json.loads(path.read_text(encoding="utf8"))
            if not corrected or "query_sha256" in report["observations"]:
                return path, report["observations"]
        raise ValueError("Run the bonus measurements first")

    public_path, public = latest("public-benchmark-*.json")
    rabitq_path, rabitq = latest("rabitq-native-*.json", corrected=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
    development = public["development"]
    effort = sorted(map(int, development))
    axes[0].plot(
        effort,
        [development[str(e)]["recall10"] for e in effort],
        "o-",
        label="60 development queries",
    )
    axes[0].scatter(
        [public["chosen_efSearch"]],
        [public["heldout"]["recall10"]],
        marker="*",
        s=160,
        color="#c34b21",
        label="60 held-out queries",
        zorder=4,
    )
    axes[0].set(
        title="Fashion-MNIST / 3,000 pixel vectors",
        xlabel="HNSW efSearch",
        ylabel="Boundary-aware recall@10",
        ylim=(0.9, 1.005),
    )
    axes[0].legend(loc="lower right", fontsize=8)
    seeds = [str(row["seed"]) for row in rabitq["scratch"]]
    x = list(range(len(seeds)))
    axes[1].bar(
        [i - 0.18 for i in x],
        [r["recall10"] for r in rabitq["scratch"]],
        width=0.36,
        label="One-bit estimator",
    )
    axes[1].bar(
        [i + 0.18 for i in x],
        [r["rescored_recall10"] for r in rabitq["scratch"]],
        width=0.36,
        label="100-candidate exact rescore",
        color="#178275",
    )
    axes[1].set(
        title="RaBitQ core / 1,000 MiniLM vectors",
        xlabel="Rotation seed",
        ylabel="Boundary-aware recall@10",
        ylim=(0, 1.05),
        xticks=x,
        xticklabels=seeds,
    )
    axes[1].legend(loc="lower right", fontsize=8)
    for axis in axes:
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    fig.suptitle("Small reproducible experiments; different datasets and protocols", fontsize=12)
    fig.text(
        0.5,
        -0.035,
        "RaBitQ: 40 frozen queries; full vectors retained for rescoring. These are not paper-scale replications.",
        ha="center",
        fontsize=9,
    )
    path = ROOT / "results/plots/bonus_research.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    atomic_json(
        path.with_suffix(".json"),
        {
            "sources": [
                str(p.relative_to(ROOT)).replace("\\", "/") for p in [public_path, rabitq_path]
            ]
        },
    )
    print(path)


if __name__ == "__main__":
    main()
