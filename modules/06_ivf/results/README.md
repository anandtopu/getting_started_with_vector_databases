# 06_ivf · measured results

Windows-11-10.0.26300-SP0, Python 3.12.13, Intel64 Family 6 Model 198 Stepping 2, GenuineIntel. The catalog benchmarks use stored MiniLM vectors, one numerical thread, and independently computed eligible neighbors.

| Family / raw held-out run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Index payload bytes |
|---|---:|---:|---:|---:|---:|
| [exact](../../../results/runs/tier2-exact-test-20261104T230422-f02515ab.json) | 1.000 | 0.732 | 1.197 / 1.718 | 790.1 ± 55.6 | — |
| [ivf](../../../results/runs/tier2-ivf-test-20261104T230923-db27c361.json) | 0.864 | 0.847 | 0.161 / 0.429 | 4561.4 ± 667.8 | 28,576 |
| [faiss-ivf](../../../results/runs/tier2-faiss-ivf-test-20261104T230429-701b6a91.json) | 0.996 | 0.732 | 0.070 / 0.362 | 7532.0 ± 697.1 | 1,568,843 |

![Development recall versus serial throughput](development.png)

The plot uses development queries. The table uses the separate test split with parameters frozen after development. Each raw file identifies the query count, split, hardware, dependency versions, source hashes, warm-ups, repeated latencies, insertion/build time and sampled RSS. Native payloads use serialized index sizes. Scratch payloads count algorithm-specific data structures, excluding interpreter overhead and the retained original vectors. The saved snapshot contains records and the build recipe; reload rebuilds the index.

| Development run | Parameters | Recall@10 | Serial QPS |
|---|---|---:|---:|
| [exact](../../../results/runs/tier2-exact-20261104T230420-d5c337d7.json) | defaults | 1.000 | 847.0 |
| [ivf](../../../results/runs/tier2-ivf-000-20261104T230914-8faf6599.json) | nlist=16, nprobe=1 | 0.809 | 4206.4 |
| [ivf](../../../results/runs/tier2-ivf-001-20261104T230916-45bf8842.json) | nlist=16, nprobe=4 | 0.969 | 2444.3 |
| [ivf](../../../results/runs/tier2-ivf-002-20261104T230919-726fb209.json) | nlist=16, nprobe=12 | 1.000 | 1659.5 |
| [ivf](../../../results/runs/tier2-ivf-003-20261104T230921-1a53cb7b.json) | nlist=16, nprobe=16 | 1.000 | 1201.8 |
| [faiss-ivf](../../../results/runs/tier2-faiss-ivf-20261104T230427-c9b99b6e.json) | nlist=16, nprobe=4 | 1.000 | 7559.7 |

[Raw lesson observation](lesson-06_ivf-8b9a0f06.json)

- For q000, {'nlist': 12, 'nprobe': 1}: recall 1.00, index payload 20,032 bytes, median retrieval 0.061 ms.
- For q000, {'nlist': 12, 'nprobe': 4}: recall 1.00, index payload 20,032 bytes, median retrieval 0.083 ms.
- For q000, {'nlist': 12, 'nprobe': 12}: recall 1.00, index payload 20,032 bytes, median retrieval 0.134 ms.

[Central leaderboard](../../../results/leaderboard.md) · [Tier 2 checkpoint analysis](../../../checkpoints/tier2/results/README.md).
