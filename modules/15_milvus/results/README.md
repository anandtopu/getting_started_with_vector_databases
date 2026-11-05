# 15_milvus · measured results

The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.

| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |
|---|---:|---:|---:|---:|---:|---:|
| [milvus](../../../results/runs/tier3-milvus-20261105T001302-95d082cf.json) | 1.000 | 0.750 | 4.312 / 6.387 | 219.4 ± 11.2 | 216.2 | 1.05 |

[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).

## Lesson experiments

- [milvus · {'index': 'FLAT'} · vector](lesson-milvus-20261105T132212-85a0a759.json) measured recall 1.000, nDCG 0.667 and p95 3.564 ms on its smaller lesson workload.
- [milvus · {'index': 'HNSW'} · vector](lesson-milvus-20261105T132220-ada93f37.json) measured recall 1.000, nDCG 0.667 and p95 3.198 ms on its smaller lesson workload.
- [milvus · {'index': 'IVF_FLAT'} · vector](lesson-milvus-20261105T132229-3470840a.json) measured recall 1.000, nDCG 0.667 and p95 2.785 ms on its smaller lesson workload.
- [milvus-consistency](milvus-consistency-6e35184a.json) records the native observation and source identity.
- [milvus-diskann](milvus-diskann-9bb41207.json) records the native observation and source identity.
- [milvus-retirement](milvus-retirement-b5fc7697.json) records the native observation and source identity.

## Native execution evidence

- [milvus](../../../results/features/milvus-df533956.json)
- [milvus_consistency](../../../results/features/milvus_consistency-df533956.json)
- [milvus_hybrid](../../../results/features/milvus_hybrid-df533956.json)

The disk-index experiment waited for indexed_rows=4096 and pending_index_rows=0 before refreshing the loaded index and searching. The initial observation with zero indexed rows is retained in the work cache as a failed readiness assumption.

These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.
