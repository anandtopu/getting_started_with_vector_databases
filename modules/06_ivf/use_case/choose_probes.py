"""Select a probe budget for a catalog search.

Concepts: Select a probe budget for a catalog search.
Run: uv run python modules/06_ivf/use_case/choose_probes.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

from common.index_lessons import trial


def main():
    rows = [trial("ivf", nlist=12, nprobe=p) for p in (1, 3, 6, 12)]
    feasible = [r for r in rows if r["recall"] >= 0.90]
    best = min(feasible, key=lambda r: r["parameters"]["nprobe"])
    print("smallest probe count meeting the single-query target", best)
    assert rows[-1]["recall"] == 1


if __name__ == "__main__":
    main()
