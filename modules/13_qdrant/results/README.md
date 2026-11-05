# 13_qdrant · measured results

The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.

| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |
|---|---:|---:|---:|---:|---:|---:|
| [qdrant](../../../results/runs/tier3-qdrant-20261105T001155-ea7545a5.json) | 1.000 | 0.750 | 10.108 / 26.429 | 87.7 ± 7.3 | 413.0 | 1.05 |

[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).

## Lesson experiments

- [qdrant · {'quantize': False} · vector](lesson-qdrant-20261105T132127-776657c2.json) measured recall 1.000, nDCG 1.000 and p95 34.626 ms on its smaller lesson workload.
- [qdrant · {'quantize': True} · vector](lesson-qdrant-20261105T132130-4bedc103.json) measured recall 1.000, nDCG 1.000 and p95 27.522 ms on its smaller lesson workload.
- [qdrant-seller-scope](qdrant-seller-scope-e6cab9d1.json) records the native observation and source identity.

## Native execution evidence

- [qdrant](../../../results/features/qdrant-df533956.json)
- [qdrant_hybrid](../../../results/features/qdrant_hybrid-df533956.json)
- [qdrant_ops](../../../results/features/qdrant_ops-df533956.json)

These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.
