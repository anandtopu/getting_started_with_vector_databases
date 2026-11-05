"""Plan the reads for a strictly routed product search.

Concepts: Plan the reads for a strictly routed product search.
Run: uv run python modules/09_disk_scale/use_case/shard_budget.py
Expected: Inspect the printed IDs or measurements and the checked invariant.
CPU: seconds on the included small workload. Uses local data; no Docker or model download.
"""

import math


def main():
    products, dim, shards = 1_000_000, 32, 8
    per_shard = math.ceil(products / shards) * dim
    print("bytes for one balanced region shard", per_shard, "bytes for all", shards * per_shard)
    print("read amplification for a single 32-byte record in a 4096-byte page", 4096 // dim)
    assert per_shard == 4_000_000


if __name__ == "__main__":
    main()
