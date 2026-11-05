# 11_embedded · measured results

The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.

| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |
|---|---:|---:|---:|---:|---:|---:|
| [chroma](../../../results/runs/tier3-chroma-20261105T001122-70b19ef3.json) | 1.000 | 0.750 | 0.479 / 1.281 | 1609.2 ± 78.7 | 270.5 | 1.05 |
| [lancedb](../../../results/runs/tier3-lancedb-20261105T001132-09e2cc31.json) | 1.000 | 0.750 | 3.339 / 6.757 | 250.5 ± 8.7 | 314.2 | 1.05 |
| [sqlite-vec](../../../results/runs/tier3-sqlite-vec-20261105T001135-3eb8990a.json) | 1.000 | 0.750 | 0.374 / 0.784 | 2194.1 ± 108.2 | 327.3 | 1.00 |
| [duckdb](../../../results/runs/tier3-duckdb-20261105T001141-ce734dc5.json) | 1.000 | 0.750 | 1.540 / 3.503 | 511.0 ± 50.2 | 385.4 | 1.05 |

[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).

## Lesson experiments

- [chroma · {} · vector](lesson-chroma-20261105T132050-f9bb87da.json) measured recall 1.000, nDCG 0.667 and p95 0.976 ms on its smaller lesson workload.
- [duckdb · {} · vector](lesson-duckdb-20261105T132309-ba377ef9.json) measured recall 1.000, nDCG 0.667 and p95 2.402 ms on its smaller lesson workload.
- [lancedb · {} · vector](lesson-lancedb-20261105T132053-f6e24543.json) measured recall 1.000, nDCG 0.667 and p95 5.756 ms on its smaller lesson workload.
- [sqlite-vec · {} · vector](lesson-sqlite-vec-20261105T132311-d5870596.json) measured recall 1.000, nDCG 0.667 and p95 0.399 ms on its smaller lesson workload.
- [embedded-restore](embedded-restore-2d097d8b.json) records the native observation and source identity.

## Native execution evidence

- [chroma](../../../results/features/chroma-df533956.json)
- [duckdb_vss](../../../results/features/duckdb_vss-df533956.json)
- [lancedb](../../../results/features/lancedb-df533956.json)
- [sqlite_vec](../../../results/features/sqlite_vec-df533956.json)

These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.
