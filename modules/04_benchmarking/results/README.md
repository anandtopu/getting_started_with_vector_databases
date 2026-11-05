# Module 04: measured results

These are executed measurements on Windows 11, Python 3.12.13, Intel family 6 model 198, 24 reported cores, 31.46 GiB RAM. Timings are local observations, not targets for another laptop. Teaching diagnostics are separated from shared-harness retrieval results. Raw files contain hardware, versions, code identity, timestamp, and measurements.

## Lesson observations

LanceDB, one unindexed q000 query: neighbor recall 1.000, precision 1.000, reciprocal rank 1.000, nDCG 1.000. Single-query diagnostic, not an engine throughput measurement. [Raw diagnostic](lancedb_quality-9782fb37.json).

Exact semantic precision@5 was **1.0**; returning the first five IDs scored **0.2**. The cheaper policy ignores the request. [Raw diagnostic](quality_tradeoff-ac6ab3da.json).

## Shared retrieval baselines

Each configuration uses 20 warm-ups and five repetitions over 100 queries, with one numerical-library thread and serial concurrency. Input sizes, query types, metrics, and models can differ across these rows; compare only matching groups in the central leaderboard. Cache and PCA labels designate accompanying retrieval workloads, not inference/PCA timing.

| Configuration / raw run | Records | Recall@10 | nDCG@10 | p50 ms | p95 ms | QPS ± SD |
|---|---:|---:|---:|---:|---:|---:|
| [quality_metrics](../../../results/runs/quality-metrics-20261104T223926-8d9d426e.json) | 1,000 | 1.0000 | 0.6586 | 0.480 | 0.634 | 1960.5 ± 31.0 |
| [benchmark_method](../../../results/runs/benchmark-method-20261104T223931-d8ebddb7.json) | 1,000 | 1.0000 | 0.8402 | 0.481 | 1.043 | 1569.4 ± 67.5 |
| [faiss_exact](../../../results/runs/faiss-exact-20261104T223936-4644c6de.json) | 1,000 | 1.0000 | 0.8402 | 0.360 | 1.059 | 1928.2 ± 51.1 |

[Recall/QPS plot for the first row](../../../results/plots/recall_qps_6f0346883012ea6d.png) · [Full leaderboard](../../../results/leaderboard.md) · [Method and limitations](../../../results/README.md).

There was no previous tested version on this exact lesson workload before Phase 3. Earlier 10k catalog and hashing-fixture runs are retained in their own groups; their timings cannot establish an improvement on this workload.

On the comparable 1k catalog runs, TinyVec measured 1569.4 serial QPS versus 1928.2 for the FAISS flat adapter. Both reached 1.000 neighbor recall. This includes the adapter's stable tie sorting and filtered temporary-index construction. It does not establish a universal winner or a native FAISS-only limit.
