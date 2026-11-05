"""Show uncertainty and why repeated timings are not independent queries.
Concepts: ground truth and evaluation.
Run: uv run python modules/bonus/B3_research_benchmarks/examples/03_measure.py
Expected: assertions pass, then measured values or a clearly labeled illustrative result.
CPU: seconds to a minute; frozen MiniLM or explicit public subset, no model downloads.
Native profiles and optional packages are described in README.md.
"""

import numpy as np


def main() -> None:
    per_query = np.array([1.0, 0.9, 0.8, 1.0, 0.7, 1.0, 0.9, 0.8, 1.0, 0.9])
    rng = np.random.default_rng(42)
    bootstrap = [rng.choice(per_query, len(per_query), replace=True).mean() for _ in range(2000)]
    lo, hi = np.percentile(bootstrap, [2.5, 97.5])
    print(
        {
            "illustrative_recall": per_query.mean(),
            "query_bootstrap_interval": [lo, hi],
            "distinct_queries": len(per_query),
        }
    )
    assert lo <= per_query.mean() <= hi
    print(
        "These illustrative scores are not public-dataset measurements. Bootstrap queries, not repeated timestamps."
    )


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
