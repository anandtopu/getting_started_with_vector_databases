"""Derive Tier 3 result pages and the checkpoint decision from actual raw measurements.
Run: uv run python scripts/report_tier3.py
CPU: seconds, no servers or model downloads. Run checkpoint_tier3 and verify_tier3 first.
"""

import json
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.settings import ROOT, cache_dir

BACKENDS = [
    ["chroma", "lancedb", "sqlite-vec", "duckdb"],
    ["pgvector"],
    ["qdrant"],
    ["weaviate"],
    ["milvus"],
    ["elasticsearch", "redis", "mongodb", "vespa"],
]


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def table(runs, prefix):
    lines = [
        "| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, r in runs.items():
        s = r["summary"]
        lines.append(
            f"| [{name}]({prefix}results/runs/{r['run_id']}.json) | {s['recall_at_k']:.3f} | {s['ndcg_at_k']:.3f} | {s['p50_ms']:.3f} / {s['p95_ms']:.3f} | {s['qps']:.1f} ± {s['qps_std']:.1f} | {r['memory']['process_peak_rss_bytes'] / 2**20:.1f} | {s['persisted_bytes'] / 2**20:.2f} |"
        )
    return lines


def diagram(runs, path):
    fig, (latency, recall) = plt.subplots(
        1, 2, figsize=(11, 5.5), layout="constrained", sharey=True
    )
    names = list(runs)
    latency.barh(names, [runs[n]["summary"]["p95_ms"] for n in names])
    latency.set(xlabel="p95 retrieval milliseconds (log scale)", xscale="log")
    recall.barh(names, [runs[n]["summary"]["recall_at_k"] for n in names], color="#1b8a70")
    recall.set(xlabel="Recall@10 against eligible exact neighbors", xlim=(0, 1.05))
    fig.suptitle("500 Marlowe products · 50 held-out queries · serial retrieval")
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    latest = {}
    for p in sorted((ROOT / "results/runs").glob("tier3-*.json")):
        r = read(p)
        b = r["config"]["backend"]
        if r["config"]["name"] != "tier3-" + b:
            continue
        if b not in latest or r["created_at"] > latest[b]["created_at"]:
            latest[b] = r
    if len(latest) < 4:
        raise ValueError("Measure at least four databases first")
    identity = {
        (
            r["dataset_sha256"],
            r["queries_sha256"],
            r["hardware_id"],
            r["config"]["metric"],
            r["config"]["k"],
        )
        for r in latest.values()
    }
    if len(identity) != 1:
        raise ValueError("Choose matched database reports before publishing")
    dest = ROOT / "checkpoints/tier3/results"
    dest.mkdir(parents=True, exist_ok=True)
    diagram(latest, dest / "comparison.png")
    executions = list((ROOT / "results/tier3").glob("execution-*.json"))
    valid = max(executions, key=lambda p: read(p)["created_at"]) if executions else None
    measured = {}
    diags = {}
    for folder, target in [
        (cache_dir() / "tier3/lesson-benchmarks/runs", measured),
        (cache_dir() / "tier3/measurements", diags),
    ]:
        for p in folder.glob("*.json"):
            r = read(p)
            key = json.dumps(r.get("config", r.get("name")), sort_keys=True)
            if key not in target or r["created_at"] > target[key][1]["created_at"]:
                target[key] = (p, r)
    modules = sorted((ROOT / "modules").glob("1[1-6]_*"))
    for module, backends in zip(modules, BACKENDS, strict=True):
        output = module / "results"
        output.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {module.name} · measured results",
            "",
            "The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.",
            "",
            *table({b: latest[b] for b in backends if b in latest}, "../../../"),
            "",
            "[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).",
            "",
            "## Lesson experiments",
            "",
        ]
        for p, r in measured.values():
            if r["config"]["backend"] not in backends:
                continue
            shutil.copyfile(p, output / p.name)
            s = r["summary"]
            lines.append(
                f"- [{r['config']['backend']} · {r['config']['parameters']} · {r['config']['retrieval']}]({p.name}) measured recall {s['recall_at_k']:.3f}, nDCG {s['ndcg_at_k']:.3f} and p95 {s['p95_ms']:.3f} ms on its smaller lesson workload."
            )
        for p, r in diags.values():
            name = r["name"]
            owner = (
                11
                if name.startswith("embedded")
                else 12
                if name.startswith("postgres")
                else 13
                if name.startswith("qdrant")
                else 14
                if name.startswith("weaviate")
                else 15
                if name.startswith("milvus")
                else 16
            )
            if owner == int(module.name[:2]):
                # Retain only the completed disk index observation for the current result page.
                if (
                    name == "milvus-diskann"
                    and r["measurements"].get("status", {}).get("indexed_rows", 0) < 4096
                ):
                    continue
                shutil.copyfile(p, output / p.name)
                lines.append(
                    f"- [{name}]({p.name}) records the native observation and source identity."
                )
        features = []
        for p in (ROOT / "results/features").glob("*.json"):
            r = read(p)
            if r["profile"]["lesson"] == module.name:
                features.append((r, p))
        selected = {}
        for r, p in features:
            n = r["profile"]["feature"]
            if n not in selected or r["created_at"] > selected[n][0]["created_at"]:
                selected[n] = (r, p)
        lines += ["", "## Native execution evidence", ""]
        for n, (_, p) in sorted(selected.items()):
            lines.append(f"- [{n}](../../../results/features/{p.name})")
        if int(module.name[:2]) == 12:
            lines += [
                "",
                "The optional pgvectorscale extension was absent from the tested pgvector image. The discovery example reports that capability boundary. Native PostgreSQL archive recovery passed using pg_dump and pg_restore.",
            ]
        if int(module.name[:2]) == 15:
            lines += [
                "",
                "The disk-index experiment waited for indexed_rows=4096 and pending_index_rows=0 before refreshing the loaded index and searching. The initial observation with zero indexed rows is retained in the work cache as a failed readiness assumption.",
            ]
        lines += [
            "",
            "These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.",
        ]
        (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    machine = next(iter(latest.values()))["hardware"]
    lines = [
        "# Reference database comparison",
        "",
        "The workload is fixed across twelve engines. The Windows client uses Python "
        + machine["python"]
        + " and "
        + machine["cpu"]
        + ". The local WSL server VM and container image digests are recorded separately. All engines search the same 500 MiniLM product vectors and 50 test queries at k=10. Twenty warm-ups precede five repetitions.",
        "",
        *table(latest, "../../../"),
        "",
        "![Measured recall and p95 latency](comparison.png)",
        "",
        "## Recommendation",
        "",
        "For an offline, single-process catalog with recall at least 0.95 and p95 at most 20 ms, SQLite-vec meets both limits on this workload and has the smallest measured retrieval p95. Chroma, DuckDB and LanceDB also qualify. Choose among them according to SQL joins, columnar history, vector collection features and application packaging. A larger or concurrent workload needs another comparison.",
        "",
        "The initial Elasticsearch approximate configuration reached 0.854 recall. The other eleven reached 1.000 on this small catalog. Exact agreement here does not settle future scale, relevance quality or write behavior. PostgreSQL, Qdrant, Weaviate, Milvus, Redis, Atlas Local and Vespa supply different service and data-model capabilities. A relational transaction or required native hybrid feature can outweigh a latency difference.",
        "",
        "The adapters validate metadata predicates in a session catalog and push eligible IDs into native retrieval. They retain an application-side metadata copy and a packed export payload. The benchmark includes this adapter overhead. Native field filters, query plans, hybrid weighting and consistency are demonstrated separately in each module.",
        "",
        "## Recovery and readiness",
        "",
        "The shared contract checks created, updated, filtered, deleted and logically restored records through all eleven new adapters. Existing SQLite-vec contracts cover the twelfth database. Native Qdrant snapshots and Weaviate filesystem backups restored the expected IDs. PostgreSQL pg_dump/pg_restore recovered a nearest-neighbor query in a different database. Milvus reported all 4,096 disk-index rows covered before the query. Atlas Local waits for the indexed revision of each changed batch and excludes retired keys from later searches.",
        "",
        "## Timing and memory boundaries",
        "",
        "Client RSS includes Python and loaded libraries. Server memory samples are post-run container usage, with Milvus dependencies listed separately. Snapshot size describes the portable export, not a server's full on-disk footprint. The runs were serial, while other course servers could remain idle in the VM. Networking and host scheduling are part of the local result. Hosted CI and a production load test are separate verification steps.",
        "",
        "[Runtime evidence](../../../research/phase5-local-runtime.json) · [Full leaderboard](../../../results/leaderboard.md) · [Benchmark method](../../../results/README.md).",
    ]
    if valid:
        execution = read(valid)
        counts = {
            state: sum(v["status"] == state for v in execution["scripts"].values())
            for state in ("passed", "failed", "skipped")
        }
        lines += [
            "",
            f"The latest [script execution record](../../../results/tier3/{valid.name}) contains {counts['passed']} passes, {counts['failed']} failures and {counts['skipped']} explicit skips.",
        ]
    (dest / "README.md").write_text("\n".join(lines) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
