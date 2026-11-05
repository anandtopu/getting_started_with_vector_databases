"""Choose an engine against a measured recall floor and latency budget.

Run: uv run python modules/16_landscape/use_case/select_a_database.py
Concepts: Choose an engine against a measured recall floor and latency budget.
Expected: the eligible product IDs or recovery decision shown in the README.
CPU: about 2–90 seconds, depending on the profile and index. Models: included vectors; optional local caption model only for the generation example. Marlowe local inputs; no database server required.
"""

import json

from common.settings import ROOT


def main() -> None:
    # KEY IDEA: Choose an engine against a measured recall floor and latency budget.
    latest = {}
    for file in sorted((ROOT / "results/runs").glob("tier3-*.json")):
        r = json.loads(file.read_text(encoding="utf-8"))
        if (
            r["config"]["name"] == "tier3-" + r["config"]["backend"]
            and r["config"]["retrieval"] == "vector"
        ):
            latest[r["config"]["backend"]] = r
    assert len(latest) >= 4
    groups = {(r["dataset_sha256"], r["queries_sha256"], r["hardware_id"]) for r in latest.values()}
    assert len(groups) == 1, "Compare runs from one matched group"
    eligible = [
        r
        for r in latest.values()
        if r["summary"]["recall_at_k"] >= 0.95 and r["summary"]["p95_ms"] <= 20
    ]
    print(
        "engines meeting recall 0.95 and 20ms p95", sorted(r["config"]["backend"] for r in eligible)
    )
    print(
        "A user's transactions, search features and operational capacity determine the final choice."
    )


if __name__ == "__main__":
    main()
