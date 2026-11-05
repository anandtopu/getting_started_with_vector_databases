# 14_weaviate · measured results

The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.

| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |
|---|---:|---:|---:|---:|---:|---:|
| [weaviate](../../../results/runs/tier3-weaviate-20261105T001200-a06d764c.json) | 1.000 | 0.750 | 1.017 / 43.265 | 264.0 ± 130.8 | 453.3 | 1.05 |

[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).

## Lesson experiments

- [weaviate · {'alpha': 0.0} · hybrid](lesson-weaviate-20261105T132142-84e07f56.json) measured recall 0.458, nDCG 1.000 and p95 4.065 ms on its smaller lesson workload.
- [weaviate · {'alpha': 0.5} · hybrid](lesson-weaviate-20261105T132145-7d8fbd4d.json) measured recall 0.500, nDCG 1.000 and p95 3.959 ms on its smaller lesson workload.
- [weaviate · {'alpha': 1.0} · hybrid](lesson-weaviate-20261105T132147-bad471d2.json) measured recall 1.000, nDCG 1.000 and p95 3.053 ms on its smaller lesson workload.
- [weaviate-local-generation](weaviate-local-generation-959aa13e.json) records the native observation and source identity.
- [weaviate-sku-meaning](weaviate-sku-meaning-4e4e92c3.json) records the native observation and source identity.

## Native execution evidence

- [weaviate](../../../results/features/weaviate-df533956.json)
- [weaviate_generation](../../../results/features/weaviate_generation-df533956.json)
- [weaviate_ops](../../../results/features/weaviate_ops-df533956.json)

These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.
