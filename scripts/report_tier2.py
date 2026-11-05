"""Build lesson result pages and checkpoint analysis from measured Tier 2 artifacts.
Run: uv run python scripts/report_tier2.py
CPU: seconds, no models or Docker. Run the checkpoint and measure examples first.
"""

import json
import shutil

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.settings import ROOT, cache_dir

FAMILIES = [
    ["exact", "lsh", "faiss-lsh"],
    ["exact", "ivf", "faiss-ivf"],
    ["exact", "hnsw", "faiss-hnsw", "usearch", "hnswlib"],
    ["exact", "scalar", "binary", "pq", "faiss-ivfpq"],
    [],
    ["filter-post", "filter-traverse", "filter-adaptive", "hybrid-rrf"],
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def raw(key):
    return read(ROOT / "results/runs" / f"{key}.json")


def table(families, choices, prefix):
    lines = [
        "| Family / raw held-out run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Index payload bytes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for family in families:
        if family not in choices:
            continue
        rid = choices[family]["test"]
        result = raw(rid)
        s = result["summary"]
        payload = s.get("index_payload_bytes")
        lines.append(
            f"| [{family}]({prefix}results/runs/{rid}.json) | {s['recall_at_k']:.3f} | {s['ndcg_at_k']:.3f} | {s['p50_ms']:.3f} / {s['p95_ms']:.3f} | {s['qps']:.1f} ± {s['qps_std']:.1f} | {payload:,} |"
            if payload is not None
            else f"| [{family}]({prefix}results/runs/{rid}.json) | {s['recall_at_k']:.3f} | {s['ndcg_at_k']:.3f} | {s['p50_ms']:.3f} / {s['p95_ms']:.3f} | {s['qps']:.1f} ± {s['qps_std']:.1f} | — |"
        )
    return lines


def plot(directory, choices, families):
    fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
    for family in families:
        runs = [raw(rid) for rid in choices[family]["development"]]
        groups = {}
        for r in runs:
            p = r["config"]["parameters"]
            group = (
                p.get("M"),
                p.get("efConstruction"),
                p.get("nprobe") if family == "faiss-ivfpq" else None,
            )
            groups.setdefault(group, []).append(r)
        for group, series in groups.items():
            names = [
                f"{key}={v}"
                for key, v in zip(("M", "efC", "probes"), group, strict=True)
                if v is not None
            ]
            ax.plot(
                [r["summary"]["qps"] for r in series],
                [r["summary"]["recall_at_k"] for r in series],
                marker="o",
                label=" ".join([family, *names]),
            )
    ax.set(
        xlabel="Serial queries per second",
        ylabel="Tie-aware recall@10",
        ylim=(0, 1.04),
        title="Development queries · 1,000 catalog products",
    )
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.2)
    fig.savefig(directory / "development.png", dpi=150)
    plt.close(fig)


def diagnostic(name, dest):
    files = [(read(p), p) for p in (cache_dir() / "tier2/measurements").glob(name + "-*.json")]
    files.extend((read(p), p) for p in dest.glob(name + "-*.json"))
    if not files:
        raise ValueError(f"Run the lesson measurement first: {name}")
    doc, path = max(files, key=lambda t: t[0]["created_at"])
    destination = dest / path.name
    if destination.resolve() != path.resolve():
        shutil.copyfile(path, destination)
    return doc["measurements"], path.name


def main():
    choices = {}
    decision_files = list((ROOT / "results/tier2").glob("decisions-*.json"))
    for p in decision_files:
        for row in read(p):
            if (
                row["family"] not in choices
                or raw(row["test"])["created_at"]
                > raw(choices[row["family"]]["test"])["created_at"]
            ):
                choices[row["family"]] = row
    mods = sorted(m for m in (ROOT / "modules").glob("[0-9][0-9]_*") if 5 <= int(m.name[:2]) <= 10)
    for index, (module, names) in enumerate(zip(mods, FAMILIES, strict=True)):
        names = [family for family in names if family in choices]
        dest = module / "results"
        dest.mkdir(parents=True, exist_ok=True)
        machine = raw(choices["exact"]["test"])["hardware"]
        context = f"{machine['os']}, Python {machine['python']}, {machine['cpu']}. "
        context += (
            "The catalog benchmarks use stored MiniLM vectors, one numerical thread, and independently computed eligible neighbors."
            if names
            else "The generated disk workload uses int8 codes and independent float ground truth. Storage fragment costs are modeled separately."
        )
        lines = [f"# {module.name} · measured results", "", context, ""]
        if names:
            lines += table(names, choices, "../../../")
            plot(dest, choices, names)
            lines += [
                "",
                "![Development recall versus serial throughput](development.png)",
                "",
                "The plot uses development queries. The table uses the separate test split with parameters frozen after development. Each raw file identifies the query count, split, hardware, dependency versions, source hashes, warm-ups, repeated latencies, insertion/build time and sampled RSS. Native payloads use serialized index sizes. Scratch payloads count algorithm-specific data structures, excluding interpreter overhead and the retained original vectors. The saved snapshot contains records and the build recipe; reload rebuilds the index.",
                "",
            ]
            lines.extend(
                ["| Development run | Parameters | Recall@10 | Serial QPS |", "|---|---|---:|---:|"]
            )
            for family in names:
                for rid in choices[family]["development"]:
                    run = raw(rid)
                    settings = (
                        ", ".join(
                            f"{k}={v}"
                            for k, v in run["config"]["parameters"].items()
                            if k != "kind"
                        )
                        or "defaults"
                    )
                    lines.append(
                        f"| [{family}](../../../results/runs/{rid}.json) | {settings} | {run['summary']['recall_at_k']:.3f} | {run['summary']['qps']:.1f} |"
                    )
            lines.append("")
        key = "disk-scale" if index == 4 else "lesson-" + module.name
        measure, filename = diagnostic(key, dest)
        lines += [f"[Raw lesson observation]({filename})", ""]
        if index == 4:
            page, source = diagnostic("page-reads", dest)
            times = np.array(measure["query_seconds"]) * 1000
            lines += [
                f"The generated workload contains {measure['rows']:,} unit vectors of {measure['dimensions']} dimensions. The int8 file occupied {measure['file_bytes']:,} bytes including its header. Five queries averaged {np.mean(measure['recall_at_10']):.3f} recall@10 against the uncompressed float reference. Median scan time was {np.median(times):.1f} ms. Peak process RSS was {measure['memory']['process_peak_rss_bytes'] / 2**20:.1f} MiB. File generation plus independent truth took {measure['build_and_float_truth_seconds']:.2f} s. OS page cache state was uncontrolled.",
                "",
                f"In the separate [page-read trace]({source}), {page['actual_reads']} real adjacency records produced recall {page['recall_at_10']:.2f}. The object-fragment figures are modeled bytes for those reads. No cloud requests were made.",
            ]
        elif index == 3:
            prefixes = measure["observations"]["qwen_prefixes"]
            base = set(prefixes["1024"]["top10"])
            lines += [
                "Qwen prefix comparison on one query, relative to its own full 1024-dimensional ranking:",
                "",
                "| Dimensions | Neighbor overlap@10 | Float32 bytes for all 128 documents |",
                "|---:|---:|---:|",
            ]
            for width, p in prefixes.items():
                lines.append(
                    f"| {width} | {len(base.intersection(p['top10'])) / 10:.1f} | {p['vector_bytes']:,} |"
                )
        elif index == 5:
            obs = measure["observations"]
            lines += [
                f"The cached cross-encoder rescored twelve candidates on q000. nDCG@10 was {obs['ndcg_before']:.3f} before reranking and {obs['ndcg_after']:.3f} after. This single query is a diagnostic; the table above measures keyword and filtered query types."
            ]
        else:
            for obs in measure["observations"]:
                lines.append(
                    f"- For q000, {obs['parameters']}: recall {obs['recall']:.2f}, index payload {obs['index_payload_bytes']:,} bytes, median retrieval {obs['timings']['median_ms']:.3f} ms."
                )
        lines.extend(
            [
                "",
                "[Central leaderboard](../../../results/leaderboard.md) · [Tier 2 checkpoint analysis](../../../checkpoints/tier2/results/README.md).",
            ]
        )
        (dest / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    output = ROOT / "checkpoints/tier2/results"
    output.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Reference checkpoint · choose an index for Marlowe",
        "",
        "The development rule chooses the highest measured serial QPS among configurations meeting the family's recall floor, or the highest recall if none qualify. The catalog and deterministic hashing fixture are tuned separately in the final scratch-index run. Hashing tests mechanics. Its scores do not establish semantic quality.",
        "",
        "| TinyVec family | Planned fixture floor | Held-out fixture recall | Catalog recall | Catalog parameters |",
        "|---|---:|---:|---:|---|",
    ]
    for name in ("lsh", "ivf", "hnsw", "pq"):
        row = choices[name]
        held = raw(row["test"])
        lines.append(
            f"| {name} | {row['target']:.2f} | [{row['fixture_recall']:.3f}](../../../results/runs/{row['fixture']}.json) | [{row['recall']:.3f}](../../../results/runs/{row['test']}.json) | `{held['config']['parameters']}` |"
        )
    lines += [
        "",
        "## Native comparisons",
        "",
        *table(
            ["exact", "ivf", "hnsw", "pq", "faiss-ivf", "faiss-hnsw", "hnswlib", "usearch"],
            choices,
            "../../../",
        ),
        "",
        "## Decision",
        "",
        f"For a 0.90 catalog recall requirement, the measured PQ shortlist reached {choices['pq']['recall']:.3f}. Compare its QPS and p95 with the exact baseline before accepting the extra training and memory cost. Native graph libraries meeting the same floor in this run: {', '.join(n for n in ('faiss-hnsw', 'hnswlib', 'usearch') if n in choices and choices[n]['recall'] >= 0.90) or 'none'}.",
        "",
        f"The teaching graph reached {choices['hnsw']['fixture_recall']:.3f} against the {choices['hnsw']['target']:.3f} fixture floor. Its connected layer fixes unreachable clusters, but a finite search beam can still stop early. The [earlier proximity-only graph](../../../results/runs/tier2-hnsw-fixture-test-20261104T230505-747688f0.json) achieved 0.414. The graph structure was revised after seeing that miss, so a second test on the same split is a regression check. A fresh query set is needed for an independent estimate.",
        "",
        "For strict metadata filters, inspect the [filtered and keyword measurements](../../../modules/10_filtering_hybrid/results/README.md). A graph can traverse ineligible bridges while returning eligible hits. The adaptive alternative scans small eligible sets exactly. For SKU lookups, compare judged relevance, because moving away from the exact dense ranking may be desirable.",
        "",
        "Snapshot bytes include original records and rebuild settings. Compressed payload bytes alone omit the cost of storing full vectors for rescoring. The million-vector disk experiment is a separate generated workload with a bounded int8 scan. Its timings cannot rank the catalog ANN engines.",
        "",
        "### Selection records",
        "",
    ]
    lines.extend(f"- [{p.name}](../../../results/tier2/{p.name})" for p in sorted(decision_files))
    validation = sorted((ROOT / "results/runs").glob("tier2-graph-budget-*.json"))
    if validation:
        lines.extend(
            [
                "",
                "### Fixed-budget graph validation",
                "",
                "The follow-up fixed a larger graph and beam before running the development split, an original-fixture regression and a new seeded product corpus. Timings are comparable only within matching workload hashes. [Procedure](../../../configs/bench/graph_validation/README.md).",
                "",
                "| Raw run | Recall@10 | p95 ms | Logical link bytes |",
                "|---|---:|---:|---:|",
            ]
        )
        for path in validation:
            report = read(path)
            summary = report["summary"]
            lines.append(
                f"| [{report['config']['name']}](../../../results/runs/{path.name}) | {summary['recall_at_k']:.3f} | {summary['p95_ms']:.3f} | {summary['index_payload_bytes']:,} |"
            )
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
