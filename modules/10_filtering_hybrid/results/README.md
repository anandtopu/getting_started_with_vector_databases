# 10_filtering_hybrid · measured results

Windows-11-10.0.26300-SP0, Python 3.12.13, Intel64 Family 6 Model 198 Stepping 2, GenuineIntel. The catalog benchmarks use stored MiniLM vectors, one numerical thread, and independently computed eligible neighbors.

| Family / raw held-out run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Index payload bytes |
|---|---:|---:|---:|---:|---:|
| [filter-post](../../../results/runs/tier2-filter-post-test-20261104T230819-16d1a10c.json) | 0.630 | 0.840 | 0.529 / 0.737 | 2073.9 ± 79.9 | 41,308 |
| [filter-traverse](../../../results/runs/tier2-filter-traverse-test-20261104T230826-03db3831.json) | 0.785 | 0.909 | 1.051 / 2.581 | 1037.5 ± 231.4 | 41,308 |
| [filter-adaptive](../../../results/runs/tier2-filter-adaptive-test-20261104T230812-282e4508.json) | 0.785 | 0.909 | 0.485 / 0.990 | 1919.9 ± 434.2 | 41,308 |
| [hybrid-rrf](../../../results/runs/tier2-hybrid-rrf-test-20261104T232724-9aafb104.json) | 0.870 | 1.000 | 0.563 / 0.911 | 1743.4 ± 32.7 | 28,576 |

![Development recall versus serial throughput](development.png)

The plot uses development queries. The table uses the separate test split with parameters frozen after development. Each raw file identifies the query count, split, hardware, dependency versions, source hashes, warm-ups, repeated latencies, insertion/build time and sampled RSS. Native payloads use serialized index sizes. Scratch payloads count algorithm-specific data structures, excluding interpreter overhead and the retained original vectors. The saved snapshot contains records and the build recipe; reload rebuilds the index.

| Development run | Parameters | Recall@10 | Serial QPS |
|---|---|---:|---:|
| [filter-post](../../../results/runs/tier2-filter-post-20261104T230815-bbce048b.json) | filter_policy=post | 0.684 | 1535.7 |
| [filter-traverse](../../../results/runs/tier2-filter-traverse-20261104T230823-a30e424b.json) | filter_policy=traverse | 0.835 | 1092.1 |
| [filter-adaptive](../../../results/runs/tier2-filter-adaptive-20261104T230808-d7ec2046.json) | filter_policy=adaptive | 0.835 | 3359.3 |
| [hybrid-rrf](../../../results/runs/tier2-hybrid-rrf-20261104T232722-034ad482.json) | nlist=16, nprobe=8 | 0.896 | 1676.6 |

[Raw lesson observation](lesson-10_filtering_hybrid-c2931939.json)

The cached cross-encoder rescored twelve candidates on q000. nDCG@10 was 0.870 before reranking and 0.870 after. This single query is a diagnostic; the table above measures keyword and filtered query types.

[Central leaderboard](../../../results/leaderboard.md) · [Tier 2 checkpoint analysis](../../../checkpoints/tier2/results/README.md).
