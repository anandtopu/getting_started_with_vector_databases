# 07_hnsw · measured results

Windows-11-10.0.26300-SP0, Python 3.12.13, Intel64 Family 6 Model 198 Stepping 2, GenuineIntel. The catalog benchmarks use stored MiniLM vectors, one numerical thread, and independently computed eligible neighbors.

| Family / raw held-out run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Index payload bytes |
|---|---:|---:|---:|---:|---:|
| [exact](../../../results/runs/tier2-exact-test-20261104T230422-f02515ab.json) | 1.000 | 0.732 | 1.197 / 1.718 | 790.1 ± 55.6 | — |
| [hnsw](../../../results/runs/tier2-hnsw-test-20261104T230855-d964b6b3.json) | 0.874 | 0.732 | 0.436 / 0.950 | 2052.4 ± 243.2 | 41,308 |
| [faiss-hnsw](../../../results/runs/tier2-faiss-hnsw-test-20261104T230425-df36f06e.json) | 0.996 | 0.732 | 0.067 / 0.357 | 8067.7 ± 139.1 | 1,616,914 |
| [usearch](../../../results/runs/tier2-usearch-test-20261104T230555-52fedf88.json) | 0.996 | 0.732 | 0.135 / 0.958 | 4319.2 ± 1504.3 | 1,620,972 |
| [hnswlib](../../../results/runs/tier2-hnswlib-test-20261104T230509-fa08d558.json) | 0.996 | 0.732 | 0.173 / 1.105 | 4433.5 ± 1716.1 | 1,620,920 |

![Development recall versus serial throughput](development.png)

The plot uses development queries. The table uses the separate test split with parameters frozen after development. Each raw file identifies the query count, split, hardware, dependency versions, source hashes, warm-ups, repeated latencies, insertion/build time and sampled RSS. Native payloads use serialized index sizes. Scratch payloads count algorithm-specific data structures, excluding interpreter overhead and the retained original vectors. The saved snapshot contains records and the build recipe; reload rebuilds the index.

| Development run | Parameters | Recall@10 | Serial QPS |
|---|---|---:|---:|
| [exact](../../../results/runs/tier2-exact-20261104T230420-d5c337d7.json) | defaults | 1.000 | 847.0 |
| [hnsw](../../../results/runs/tier2-hnsw-000-20261104T230829-2f279c5f.json) | M=4, efConstruction=24, efSearch=12 | 0.433 | 2926.9 |
| [hnsw](../../../results/runs/tier2-hnsw-001-20261104T230832-1662891d.json) | M=4, efConstruction=24, efSearch=48 | 0.559 | 1996.1 |
| [hnsw](../../../results/runs/tier2-hnsw-002-20261104T230835-b4f4dd92.json) | M=4, efConstruction=48, efSearch=12 | 0.444 | 3138.4 |
| [hnsw](../../../results/runs/tier2-hnsw-003-20261104T230838-7e832261.json) | M=4, efConstruction=48, efSearch=48 | 0.603 | 2143.4 |
| [hnsw](../../../results/runs/tier2-hnsw-004-20261104T230841-60eb4c2e.json) | M=8, efConstruction=24, efSearch=12 | 0.832 | 2990.5 |
| [hnsw](../../../results/runs/tier2-hnsw-005-20261104T230844-6fc333aa.json) | M=8, efConstruction=24, efSearch=48 | 0.940 | 2041.6 |
| [hnsw](../../../results/runs/tier2-hnsw-006-20261104T230848-9c8d0fb1.json) | M=8, efConstruction=48, efSearch=12 | 0.872 | 3052.8 |
| [hnsw](../../../results/runs/tier2-hnsw-007-20261104T230852-47d4d15e.json) | M=8, efConstruction=48, efSearch=48 | 0.990 | 1965.4 |
| [faiss-hnsw](../../../results/runs/tier2-faiss-hnsw-20261104T230424-e1e3cda1.json) | defaults | 0.976 | 7307.0 |
| [usearch](../../../results/runs/tier2-usearch-20261104T230553-2024cdde.json) | defaults | 0.937 | 5251.7 |
| [hnswlib](../../../results/runs/tier2-hnswlib-20261104T230507-a18664ed.json) | defaults | 0.950 | 5264.9 |

[Raw lesson observation](lesson-07_hnsw-2098852e.json)

- For q000, {'M': 6, 'efConstruction': 32, 'efSearch': 10, 'oversample': 1}: recall 1.00, index payload 13,580 bytes, median retrieval 0.102 ms.
- For q000, {'M': 6, 'efConstruction': 32, 'efSearch': 24, 'oversample': 1}: recall 1.00, index payload 13,580 bytes, median retrieval 0.139 ms.
- For q000, {'M': 6, 'efConstruction': 32, 'efSearch': 64, 'oversample': 1}: recall 1.00, index payload 13,580 bytes, median retrieval 0.285 ms.

[Central leaderboard](../../../results/leaderboard.md) · [Tier 2 checkpoint analysis](../../../checkpoints/tier2/results/README.md).
