# 16_landscape · measured results

The shared comparison uses 500 stored MiniLM product vectors, 50 test queries, twenty warm-ups and five repetitions. The recorded Windows client talks to local rootless Podman servers through loopback ports. Logical snapshots are exports read back from the database. The client RSS column excludes separate server processes.

| Engine / raw run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Client peak MiB | Logical export MiB |
|---|---:|---:|---:|---:|---:|---:|
| [elasticsearch](../../../results/runs/tier3-elasticsearch-20261105T001238-da1266c7.json) | 0.854 | 0.750 | 49.508 / 55.323 | 19.8 ± 0.2 | 241.3 | 1.05 |
| [redis](../../../results/runs/tier3-redis-20261105T001210-01916bdb.json) | 1.000 | 0.750 | 0.598 / 1.516 | 1357.9 ± 165.0 | 217.5 | 1.05 |
| [mongodb](../../../results/runs/tier3-mongodb-20261105T001301-610cef0a.json) | 1.000 | 0.750 | 2.523 / 5.053 | 351.8 ± 32.8 | 225.7 | 1.05 |
| [vespa](../../../results/runs/tier3-vespa-20261105T001412-38a9ccd6.json) | 1.000 | 0.750 | 50.630 / 280.644 | 12.7 ± 0.6 | 210.9 | 1.05 |

[All twelve databases and decision](../../../checkpoints/tier3/results/README.md) · [Runtime identities and post-run memory samples](../../../research/phase5-local-runtime.json).

## Lesson experiments

- [faiss-http](faiss-http-51424c87.json) records the native observation and source identity.

## Native execution evidence

- [elasticsearch](../../../results/features/elasticsearch-df533956.json)
- [faiss_service](../../../results/features/faiss_service-df533956.json)
- [managed_services](../../../results/features/managed_services-df533956.json)
- [mongodb_local](../../../results/features/mongodb_local-df533956.json)
- [redis_search](../../../results/features/redis_search-df533956.json)
- [vendor_benchmarks](../../../results/features/vendor_benchmarks-df533956.json)
- [vespa](../../../results/features/vespa-df533956.json)

These rows are local measurements. Whole-script times in feature records include interpreter startup, setup, assertions and teardown. Retrieval-only times are in benchmark JSON.
