"""Choose a compressed shortlist under an explicit memory budget.

Concepts: Choose a compressed shortlist under an explicit memory budget.
Run: uv run python modules/08_quantization/use_case/memory_budget.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import trial


def main():
    rows = [trial(kind, limit=640, oversample=8) for kind in ("binary", "scalar", "pq")]
    budget = 100_000
    feasible = [r for r in rows if r["index_payload_bytes"] <= budget]
    best = max(feasible, key=lambda r: r["recall"])
    print(
        "eligible code indexes",
        [(r["kind"], r["index_payload_bytes"]) for r in feasible],
        "best q000 recall",
        best["recall"],
    )
    print(
        "full rescoring vectors add", 640 * 384 * 4, "bytes; metadata and interpreter are separate"
    )


if __name__ == "__main__":
    main()
