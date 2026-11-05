# Module 00: measured results

These are executed measurements on Windows 11, Python 3.12.13, Intel family 6 model 198, 24 reported cores, 31.46 GiB RAM. Timings are local observations, not targets for another laptop. Teaching diagnostics are separated from shared-harness retrieval results. Raw files contain hardware, versions, code identity, timestamp, and measurements.

## Lesson observations

Whole-phrase matches: **0**. Useful mug warmers at five: **5**. Median saved-search wrapper time (including frozen-query lookup): 58.48 ms. [Raw diagnostic](orientation-c5e4136f.json).

## Shared retrieval baselines

Each configuration uses 20 warm-ups and five repetitions over 100 queries, with one numerical-library thread and serial concurrency. Input sizes, query types, metrics, and models can differ across these rows; compare only matching groups in the central leaderboard. Cache and PCA labels designate accompanying retrieval workloads, not inference/PCA timing.

| Configuration / raw run | Records | Recall@10 | nDCG@10 | p50 ms | p95 ms | QPS ± SD |
|---|---:|---:|---:|---:|---:|---:|
| [orientation](../../../results/runs/orientation-20261104T223854-dcfa4e33.json) | 1,000 | 1.0000 | 0.8835 | 0.450 | 0.597 | 2090.2 ± 79.6 |

[Recall/QPS plot for the first row](../../../results/plots/recall_qps_e29ae9d7b34818a1.png) · [Full leaderboard](../../../results/leaderboard.md) · [Method and limitations](../../../results/README.md).

There was no previous tested version on this exact lesson workload before Phase 3. Earlier 10k catalog and hashing-fixture runs are retained in their own groups; their timings cannot establish an improvement on this workload.
