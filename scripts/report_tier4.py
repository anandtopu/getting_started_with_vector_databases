"""Derive application tables and plots from saved observations, never invented values.
Run: uv run python scripts/report_tier4.py
CPU: seconds. Requires successful checkpoint_tier4.py parts.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from common.settings import ROOT


def latest(part):
    files = list((ROOT / "results/tier4").glob(f"{part}-*.json"))
    if not files:
        raise ValueError(f"Run checkpoint part {part} first")
    path = max(files, key=lambda p: p.stat().st_mtime_ns)
    return path, json.loads(path.read_text(encoding="utf8"))


def table(columns, rows):
    return (
        "| "
        + " | ".join(columns)
        + " |\n|"
        + "|".join(["---"] * len(columns))
        + "|\n"
        + "\n".join(
            "| " + " | ".join(f"{v:.4f}" if isinstance(v, float) else str(v) for v in row) + " |"
            for row in rows
        )
    )


def main():
    runs = {
        part: latest(part) for part in ["search", "multilingual", "rag", "recommendations", "photo"]
    }
    observations = {key: data["observations"] for key, (_, data) in runs.items()}
    destination = ROOT / "checkpoints/tier4/results"
    destination.mkdir(parents=True, exist_ok=True)
    search, multilingual, rag, rec, photo = [observations[key] for key in runs]
    search_table = table(
        ["Version", "Held-out type", "Queries", "nDCG@10", "MRR", "Precision@10"],
        [
            [r[k] for k in ["version", "type", "queries", "ndcg10", "mrr", "precision10"]]
            for r in search["held_out"]
        ],
    )
    rec_rows = []
    for weight in [1.0, 0.7, 0.3]:
        rows = [r for r in rec["recommendations"] if r.get("weight") == weight]
        rec_rows.append(
            [
                weight,
                len(rows),
                float(np.mean([r["recall10"] for r in rows])) if rows else None,
                float(np.mean([r["diversity"] for r in rows])) if rows else None,
                sum(r["seen_leaks"] for r in rows),
            ]
        )
    blocks = {
        "17_product_search": search_table
        + "\n\n"
        + table(
            ["Model on matched 500 products", "Held-out multilingual nDCG@10"],
            [[k, v] for k, v in multilingual["held_out"].items()],
        )
        + f"\n\nParser exact-match coverage: {search['parser_exact_matches']}/{search['parser_queries']}. Retrieval timing: `{json.dumps(search['timing'])}`. Only 50 held-out text queries exist in the supplied judgment set, below the preferred 100-query benchmark size. Five repetitions produce 250 timings, not 250 independent questions. Reranking is a separately timed single-pass quality diagnostic. Initial unprotected SKU reranking is preserved in the earlier raw run.\n",
        "18_rag": table(
            ["Retrieval", "Source passage recall@4"],
            [
                ["Exact", rag["exact_passage_recall4"]],
                ["IVF, 8 lists, 1 probe", rag["ann_passage_recall4"]],
                ["LSH, 10 bits, 1 table", rag["lsh_passage_recall4"]],
            ],
        )
        + "\n\nThe small corpus makes IVF easy; the narrow LSH configuration exposes candidate loss. See the raw record for per-question sources, draft answers, served excerpts, citations and generation time. [Claim-support review](../../../docs/RAG_REVIEW.md) separates citation syntax, factual support, relevance and completeness. Draft quality is insufficient for direct delivery. The application uses a transparent extractive fallback.\n",
        "19_recommendations": table(
            [
                "MMR relevance",
                "Users",
                "Future purchase recall@10",
                "Mean pairwise distance",
                "Seen leaks",
            ],
            rec_rows,
        )
        + "\n\n"
        + table(
            ["Duplicate split", "Pairs", "Threshold", "Precision", "Recall", "F1"],
            [
                [
                    split,
                    *[
                        rec["duplicates"][split][k]
                        for k in ["pairs", "threshold", "precision", "recall", "f1"]
                    ],
                ]
                for split in ["development", "test"]
            ],
        )
        + "\n\nThe original generator's first 100-user audit had zero evaluable unseen-purchase cases. The final run uses the separately labeled 700-event temporal fixture. Duplicate evaluation includes only 400 pairs with both IDs in the committed 10k catalog, excluding 1,600 unavailable pairs. The same-kind recommendation fixture and planted duplicates are easy synthetic tasks. Six review themes and ten outlier candidates are in the raw result, without human topic or anomaly labels.\n",
        "20_multimodal": table(
            ["Mode", "Held-out nDCG@10"], [[k, v] for k, v in photo["held_out"].items()]
        )
        + "\n\nThe exact query image ID is excluded from retrieval and judgments. The gallery contains 200 Pillow illustrations and repeated drawing templates. Each mode has ten held-out query families. Fusion weight 0.7 is an illustrative fixed policy, not an optimized production setting. These results do not establish quality on photographs.\n",
    }
    modules_to_parts = {
        "17_product_search": ["search", "multilingual"],
        "18_rag": ["rag"],
        "19_recommendations": ["recommendations"],
        "20_multimodal": ["photo"],
    }
    for module, block in blocks.items():
        links = " · ".join(
            f"[{part} raw JSON](../../../results/tier4/{runs[part][0].name})"
            for part in modules_to_parts[module]
        )
        text = f"# Measured application results: {module}\n\n{links}\n\n{block}\n\nBackend: **{runs[modules_to_parts[module][0]][1]['backend']}**, a single owned local Qdrant client per application evaluation. Hardware and package versions are embedded in every raw JSON. Model identities and content hashes are in the linked run's artifact manifests. Judgments are synthetic. No hosted service was used.\n\n[Comparison plot](../../../checkpoints/tier4/results/comparison.png) · [Method and reproduction](../../../checkpoints/tier4/README.md)\n"
        path = ROOT / "modules" / module / "results/README.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(text, encoding="utf8")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    kinds = sorted({r["type"] for r in search["held_out"]})
    x = np.arange(len(kinds))
    for i, version in enumerate(["v1_dense", "v2_hybrid", "v2_reranked"]):
        values = [
            next(
                r["ndcg10"]
                for r in search["held_out"]
                if r["type"] == kind and r["version"] == version
            )
            for kind in kinds
        ]
        axes[0, 0].bar(x + (i - 1) * 0.25, values, 0.25, label=version)
    axes[0, 0].set_xticks(x, kinds, rotation=15)
    axes[0, 0].set_title("10k catalog: held-out nDCG@10")
    axes[0, 0].legend(fontsize=8)
    axes[0, 1].bar(
        ["Exact", "IVF", "Narrow LSH"],
        [rag["exact_passage_recall4"], rag["ann_passage_recall4"], rag["lsh_passage_recall4"]],
    )
    axes[0, 1].set_title("80 help questions: passage recall@4")
    axes[1, 0].bar([str(r[0]) for r in rec_rows], [r[3] or 0 for r in rec_rows])
    axes[1, 0].set_title("100 synthetic users: recommendation diversity")
    axes[1, 0].set_xlabel("MMR relevance weight")
    axes[1, 1].bar(["Text to image", "Photo", "Fused"], list(photo["held_out"].values()))
    axes[1, 1].set_title("200 drawings: held-out nDCG@10, self excluded")
    for ax in axes.flat:
        ax.set_ylim(0, 1.05)
        ax.grid(axis="y", alpha=0.2)
    axes[1, 0].set_ylim(0, max(r[3] or 0 for r in rec_rows) * 1.25)
    axes[1, 0].set_ylabel("Mean pairwise cosine distance")
    for bar, row in zip(axes[1, 0].patches, rec_rows, strict=True):
        axes[1, 0].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{row[3]:.4f}",
            ha="center",
            va="bottom",
        )
    fig.suptitle("Marlowe application diagnostics · Qdrant local · synthetic judgments")
    fig.savefig(destination / "comparison.png", dpi=150)
    plt.close(fig)
    refs = "\n".join(
        f"- [{part} raw evidence](../../../results/tier4/{path.name})"
        for part, (path, _) in runs.items()
    )
    (destination / "README.md").write_text(
        f"# Tier 4 results\n\n![Application comparisons](comparison.png)\n\n{refs}\n\nEach panel uses its own stated dataset and metric. This is an application diagnostic, not a vendor ranking. See the module result pages for tables and limitations.\n",
        encoding="utf8",
    )
    print(destination)


if __name__ == "__main__":
    main()
