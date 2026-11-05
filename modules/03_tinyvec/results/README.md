# Module 03: measured results

These are executed measurements on Windows 11, Python 3.12.13, Intel family 6 model 198, 24 reported cores, 31.46 GiB RAM. Timings are local observations, not targets for another laptop. Teaching diagnostics are separated from shared-harness retrieval results. Raw files contain hardware, versions, code identity, timestamp, and measurements.

## Lesson observations

The postfiltered top-one returned **0** eligible products; exact prefiltering returned **1**. A real eligible product was lost by selecting too early. [Raw diagnostic](filter_order-7257b7d0.json).

## Shared retrieval baselines

Each configuration uses 20 warm-ups and five repetitions over 100 queries, with one numerical-library thread and serial concurrency. Input sizes, query types, metrics, and models can differ across these rows; compare only matching groups in the central leaderboard. Cache and PCA labels designate accompanying retrieval workloads, not inference/PCA timing.

| Configuration / raw run | Records | Recall@10 | nDCG@10 | p50 ms | p95 ms | QPS ± SD |
|---|---:|---:|---:|---:|---:|---:|
| [storage_crud](../../../results/runs/storage-crud-20261104T223917-ce24b2dd.json) | 1,000 | 1.0000 | 0.8753 | 0.956 | 1.117 | 1302.3 ± 39.9 |
| [exact_search](../../../results/runs/exact-search-20261104T223921-0ecc921f.json) | 1,000 | 1.0000 | 0.8402 | 0.475 | 1.090 | 1556.9 ± 39.9 |

[Recall/QPS plot for the first row](../../../results/plots/recall_qps_ec9257ec4a970d04.png) · [Full leaderboard](../../../results/leaderboard.md) · [Method and limitations](../../../results/README.md).

There was no previous tested version on this exact lesson workload before Phase 3. Earlier 10k catalog and hashing-fixture runs are retained in their own groups; their timings cannot establish an improvement on this workload.
