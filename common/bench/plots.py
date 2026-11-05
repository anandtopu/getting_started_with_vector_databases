"""A separate recall–QPS plot for each compatible experiment group."""

from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.bench.leaderboard import reports
from common.io import digest


def write_plots(directory: Path) -> list[Path]:
    groups = defaultdict(list)
    for run in reports(directory):
        key = (
            run["dataset_sha256"],
            run["queries_sha256"],
            run["hardware_id"],
            run["config"]["metric"],
            run["config"]["k"],
            run["config"]["threads"],
            run["embedding"]["space"],
            run["method"].get("recall_semantics", "strict-id"),
        )
        groups[key].append(run)
    paths = []
    (directory / "plots").mkdir(parents=True, exist_ok=True)
    for key, group in groups.items():
        fig, ax = plt.subplots(figsize=(8, 5), layout="constrained")
        families = {}
        for run in group:
            quality = run["summary"]["recall_at_k"]
            if quality is not None:
                label = run["config"]["name"]
                if len(group) > 12:
                    label = run["config"]["parameters"].get("kind", run["config"]["backend"])
                first = label not in families
                families.setdefault(label, f"C{len(families) % 10}")
                ax.errorbar(
                    run["summary"]["qps"],
                    quality,
                    xerr=run["summary"]["qps_std"],
                    fmt="o",
                    capsize=3,
                    label=label if first else "_nolegend_",
                    color=families[label],
                )
        ax.set(
            xlabel="Serial queries per second (mean ± repeated-run SD)",
            ylabel="Recall against exact neighbors",
            ylim=(0, 1.04),
            title=f"{group[0]['record_count']:,} Marlowe records · {key[3]} · k={key[4]}\nHardware {key[2]} · queries {key[1][:8]}",
        )
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
        path = directory / "plots" / f"recall_qps_{digest(key)[:16]}.png"
        fig.savefig(path, dpi=160)
        plt.close(fig)
        paths.append(path)
    return paths
