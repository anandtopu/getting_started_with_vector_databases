"""Run the same held-out catalog queries on three embedded databases and recommend locally.
Run: uv run --extra embedded python capstones/02_database_bakeoff/solution/project.py
Expected: three raw runs and a qualified recommendation. CPU: minutes; no downloads/server.
"""

from common.bench.config import BenchConfig
from common.bench.leaderboard import write_leaderboard
from common.bench.runner import run_benchmark
from common.errors import run_cli
from common.research import record
from common.settings import ROOT


def recommend(results, minimum_recall=0.95):
    eligible = [
        r
        for r in results
        if r["summary"]["recall_at_k"] is not None
        and r["summary"]["recall_at_k"] >= minimum_recall
        and r["summary"].get("errors", 0) == 0
    ]
    if not eligible:
        return {"choice": None, "reason": "No measured system met the recall gate"}
    winner = min(eligible, key=lambda r: r["summary"]["p95_ms"])
    return {
        "choice": winner["config"]["backend"],
        "reason": "Lowest observed p95 among systems meeting recall, on this local workload only",
        "run_id": winner["run_id"],
        "minimum_recall": minimum_recall,
        "limits": "Small warm-cache single-client fixture; compare operational/filter/update requirements separately",
    }


def main() -> None:
    results = []
    for backend in ["sqlite-vec", "chroma", "lancedb"]:
        config = BenchConfig(
            name="capstone-bakeoff-" + backend,
            backend=backend,
            dataset="catalog",
            limit=500,
            k=10,
            warmup=5,
            repetitions=3,
            queries=30,
            split="test",
        )
        results.append(run_benchmark(config, ROOT / "results"))
    selection = recommend(results)
    print(
        record(
            "capstone-bakeoff",
            {"runs": [r["run_id"] for r in results], "recommendation": selection},
            "python capstones/02_database_bakeoff/solution/project.py",
        )
    )
    print(selection)
    write_leaderboard(ROOT / "results")


if __name__ == "__main__":
    run_cli(main)
