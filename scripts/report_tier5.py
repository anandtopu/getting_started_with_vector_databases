"""Derive Tier 5 tables and plots from preserved raw observations.
Run: uv run python scripts/report_tier5.py
CPU: seconds. No measurements, network calls or source-result rewriting.
"""

import json

import matplotlib

from common.settings import ROOT

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = ROOT / "results/tier5"

    def latest(pattern):
        records = [(json.loads(p.read_text()), p) for p in root.glob(pattern)]
        return max(records, key=lambda pair: pair[0]["created_at"])

    checkpoint, cp = latest("checkpoint-*.json")
    cluster, cl = latest("cluster-*.json")
    monitor, mo = latest("monitoring-*.json")
    load, lp = latest("load-*/report.json")
    values = checkpoint["observations"]
    tuning = values["target_tuning"]
    recovery = values["disaster_recovery"]
    native = values["native_migration_restore"]
    rows = load["runs"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
    steady = [r for r in rows if not r["failure_injected"]]
    axes[0].plot(
        [r["users"] for r in steady], [float(r["stats"]["Requests/s"]) for r in steady], "o-"
    )
    axes[0].set(
        xlabel="Concurrent users",
        ylabel="Completed requests / second",
        title="Measured local warm-query load",
    )
    axes[1].plot([r["users"] for r in steady], [float(r["stats"]["95%"]) for r in steady], "o-")
    axes[1].set(
        xlabel="Concurrent users",
        ylabel="p95 milliseconds",
        title="All completed responses, including errors",
    )
    fig.tight_layout()
    fig.savefig(root / "load.png", dpi=160)
    plt.close(fig)
    lines = [
        "# Tier 5 measured operations",
        "",
        "These are operational diagnostics, not a cross-database throughput ranking. Raw files retain actual hardware, package versions and source provenance. Earlier runs and observed failures are preserved.",
        "",
        "## Recovery and index operations",
        "",
        f"[Checkpoint raw data]({cp.name}) · [three-node raw data]({cl.name}) · [monitoring raw data]({mo.name})",
        "",
        "| Observation | Measured result |",
        "|---|---|",
        f"| Duplicate replay | 1,000 unique live IDs; at most {values['operations']['ingestion']['max_pending_batches']} pending batches |",
        "| Scratch compaction | 2,000 physical versions to 900 live rows, with identical live view |",
        f"| SQLite bytes, delete, VACUUM | {values['sqlite_compaction']['before_bytes']:,} → {values['sqlite_compaction']['after_delete_bytes']:,} → {values['sqlite_compaction']['after_vacuum_bytes']:,} |",
        f"| Fresh-process restore | {recovery['restore_seconds_including_process_start']:.3f} s; 99 restored rows; five acknowledged writes lost; zero resurrected deletions |",
        f"| Native Qdrant snapshot | {native['snapshot_bytes']:,} bytes; {native['restore_seconds']:.3f} s restore; 499 rows after deletion |",
        f"| One peer down | Write acknowledged in {cluster['observations']['write_with_one_peer_down_seconds']:.3f} s |",
        f"| Peer rejoin | {cluster['observations']['rejoin_seconds']:.3f} s until both local shards active and both points present |",
        "| Auth/TLS | Unauthenticated request rejected, read key cannot write, untrusted CA rejected |",
        f"| Monitoring | Live TLS scrape up=1; {int(float(monitor['observations']['time_series'][0]['value'][1]))} observed series; {monitor['observations']['panels']} provisioned panels |",
        "",
        "The corrected cluster drill passes read consistency as an HTTP query parameter. Its immediate majority read returned 500 during the outage; an explicit single-replica read returned both points, and majority reads returned both after recovery. Earlier cluster records put consistency in the request body and do not establish majority-read behavior. This is a transient observation, not a general claim that majority reads cannot tolerate one failed peer. The native migration used 500 MiniLM and Qwen vectors, deleted one point in each generation, changed a real collection alias and rolled it back. The separate application router couples encoder and collection identity. A checksum establishes byte integrity, not backup authenticity. Replica recovery uses three peers on one host, not independent failure zones.",
        "",
        "## Target tuning and cache",
        "",
        f"Development queries selected nprobe={tuning['chosen_nprobe']} against recall≥0.90 and p95≤50 ms. Held-out recall@10 was **{tuning['heldout']['recall_at_10']:.3f}**, p95 **{tuning['heldout']['p95_ms']:.3f} ms**. There are only ten distinct held-out queries, each repeated three times. This measures ANN recall against exact neighbors, not semantic usefulness. No confidence interval over independent datasets is claimed.",
        "",
        f"The in-process cache experiment used {values['cache_measurement']['samples']} paired samples: cold median {values['cache_measurement']['cold_p50_ms']:.4f} ms and cached median {values['cache_measurement']['warm_p50_ms']:.4f} ms. It excludes HTTP, authentication, audit and model inference; do not compare it directly with the following table.",
        "",
        "## HTTP load and recovery",
        "",
        f"[Raw report and sibling CSV/log files]({lp.relative_to(root).as_posix()})",
        "",
        "| Users | Interrupted | Requests | Failed | Failed % | Requests/s | p50 ms | p95 ms | p99 ms |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        s = row["stats"]
        lines.append(
            f"| {row['users']} | {row['failure_injected']} | {s['Request Count']} | {s['Failure Count']} | {100 * int(s['Failure Count']) / max(1, int(s['Request Count'])):.1f} | {float(s['Requests/s']):.2f} | {s['50%']} | {s['95%']} | {s['99%']} |"
        )
    interrupted = next(r for r in rows if r["failure_injected"])
    lines += [
        "",
        f"The injected process outage took **{interrupted['recovery_seconds']:.3f} s** from after termination through an intentional two-second pause, restart and successful health response. Readiness is not the same as complete cache rewarming. Each run lasted about 20 seconds; Locust buckets percentiles and counts completed requests. Small samples and startup effects limit tail estimates. Errors include 429 admission rejection and connection failures during interruption.",
        "",
        "![Concurrency, throughput and latency](load.png)",
        "",
        "Compare throughput and tail latency together: this single-worker application retains a common service lock and serialized durable audit writes. Audit I/O now runs in a worker thread and is awaited before returning the response; the event loop remains available. Request timing includes that audit wait. Earlier runs exposed blocking audit I/O. The experiments do not isolate all remaining bottlenecks. Requests use frozen queries and a warm application cache, with no live embedding inference. Successful unfiltered results are checked for seller ownership; comprehensive endpoint/filter isolation is separately covered by the test suite.",
        "",
        "An earlier load run intentionally remains available with rejected q005 text requests: q005 is an image-query fixture and was removed from the corrected text workload. An earlier native isolation assertion incorrectly required tied results in a fixed order; the corrected assertion checks membership and its rerun passed. Failed evidence is never overwritten.",
        "",
        "## Capacity, cost and verification limits",
        "",
        "The [memory worksheet](../../docs/MEMORY_MATH.md) calculates a 102.4 GB planning budget from explicit assumptions for 10M × 768 float32 vectors, two replicas and headroom. No 10-million-vector deployment was measured. Cost inputs are hypothetical, not vendor quotes. Native server memory was not sampled in these drills.",
        "",
        "Live Qdrant metrics scraping and Grafana provisioning passed. API metrics were captured by the load test; cross-VM live API scraping and browser dashboard interaction were not executed. The [runbook](../../docs/TIER5_RUNBOOK.md) identifies the additional same-host API target. Hosted CI and other operating systems were not run locally.",
        "",
        "See [Phase 7 verification](../../docs/PHASE_7_REPORT.md) and the [Tier 5 checkpoint](../../checkpoints/tier5/README.md).",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf8")
    for module in ["21_operations", "22_performance", "23_security_reliability"]:
        target = ROOT / "modules" / module / "results/README.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"# Module {module[:2]} results\n\nRead the [measured Tier 5 tables and raw records](../../../results/tier5/README.md). The [Phase 7 report](../../../docs/PHASE_7_REPORT.md) records executed checks and limitations.\n\nReproduce the local checkpoint with `uv run python scripts/checkpoint_tier5.py`; add `--native` only after secure database setup. Load, cluster and monitoring use the explicit commands in the [runbook](../../../docs/TIER5_RUNBOOK.md). Diagnostic timings have different scopes and must not be ranked together.\n",
            encoding="utf8",
        )
    print(root / "README.md")


if __name__ == "__main__":
    main()
