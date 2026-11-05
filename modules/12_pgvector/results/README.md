# 12_pgvector · measured results

The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.

| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |
|---|---:|---:|---:|---:|---:|---:|
| [pgvector](../../../results/runs/tier3-pgvector-20261105T001147-d30658f5.json) | 1.000 | 0.750 | 2.175 / 46.665 | 92.9 ± 1.1 | 362.7 | 1.05 |

[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).

## Lesson experiments

- [pgvector · {'index': 'flat'} · vector](lesson-pgvector-20261105T132110-73265c2f.json) measured recall 1.000, nDCG 0.667 and p95 44.247 ms on its smaller lesson workload.
- [pgvector · {'index': 'hnsw'} · vector](lesson-pgvector-20261105T132112-36eba7d3.json) measured recall 1.000, nDCG 0.667 and p95 44.408 ms on its smaller lesson workload.
- [pgvector · {'index': 'ivfflat'} · vector](lesson-pgvector-20261105T132114-3f7e17a2.json) measured recall 0.717, nDCG 0.547 and p95 44.314 ms on its smaller lesson workload.
- [postgres-regional-inventory](postgres-regional-inventory-b792d590.json) records the native observation and source identity.

## Native execution evidence

- [pgvector](../../../results/features/pgvector-df533956.json)
- [pgvectorscale](../../../results/features/pgvectorscale-df533956.json)
- [postgres_hybrid](../../../results/features/postgres_hybrid-df533956.json)

The optional pgvectorscale extension was absent from the tested pgvector image. The discovery example reports that capability boundary. Native PostgreSQL archive recovery passed using pg_dump and pg_restore.

These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.
