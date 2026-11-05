# 08_quantization · measured results

Windows-11-10.0.26300-SP0, Python 3.12.13, Intel64 Family 6 Model 198 Stepping 2, GenuineIntel. The catalog benchmarks use stored MiniLM vectors, one numerical thread, and independently computed eligible neighbors.

| Family / raw held-out run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Index payload bytes |
|---|---:|---:|---:|---:|---:|
| [exact](../../../results/runs/tier2-exact-test-20261104T230422-f02515ab.json) | 1.000 | 0.732 | 1.197 / 1.718 | 790.1 ± 55.6 | — |
| [scalar](../../../results/runs/tier2-scalar-test-20261104T230550-870d1e8a.json) | 0.988 | 0.732 | 0.472 / 1.191 | 1697.5 ± 595.2 | 385,536 |
| [binary](../../../results/runs/tier2-binary-test-20261104T230418-9daa9c72.json) | 0.776 | 0.732 | 0.151 / 0.354 | 5048.0 ± 533.7 | 48,000 |
| [pq](../../../results/runs/tier2-pq-test-20261104T230952-2d0af5fe.json) | 0.924 | 0.732 | 0.135 / 0.575 | 4306.9 ± 651.4 | 32,576 |
| [faiss-ivfpq](../../../results/runs/tier2-faiss-ivfpq-test-20261104T230437-91771b69.json) | 0.848 | 0.732 | 0.070 / 0.355 | 7951.5 ± 90.3 | 61,460 |

![Development recall versus serial throughput](development.png)

The plot uses development queries. The table uses the separate test split with parameters frozen after development. Each raw file identifies the query count, split, hardware, dependency versions, source hashes, warm-ups, repeated latencies, insertion/build time and sampled RSS. Native payloads use serialized index sizes. Scratch payloads count algorithm-specific data structures, excluding interpreter overhead and the retained original vectors. The saved snapshot contains records and the build recipe; reload rebuilds the index.

| Development run | Parameters | Recall@10 | Serial QPS |
|---|---|---:|---:|
| [exact](../../../results/runs/tier2-exact-20261104T230420-d5c337d7.json) | defaults | 1.000 | 847.0 |
| [scalar](../../../results/runs/tier2-scalar-20261104T230548-39d538b7.json) | oversample=1 | 0.979 | 1928.5 |
| [binary](../../../results/runs/tier2-binary-000-20261104T230414-f20f8b6f.json) | oversample=1 | 0.450 | 5034.3 |
| [binary](../../../results/runs/tier2-binary-001-20261104T230416-0e567e62.json) | oversample=8 | 0.865 | 4991.1 |
| [pq](../../../results/runs/tier2-pq-000-20261104T230945-1f697f79.json) | parts=8, centroids=16, oversample=1 | 0.383 | 4786.5 |
| [pq](../../../results/runs/tier2-pq-001-20261104T230947-829d8c0d.json) | parts=8, centroids=16, oversample=8 | 0.980 | 3257.5 |
| [pq](../../../results/runs/tier2-pq-002-20261104T230949-b817b1f8.json) | parts=8, centroids=16, oversample=32 | 0.999 | 2484.3 |
| [faiss-ivfpq](../../../results/runs/tier2-faiss-ivfpq-000-20261104T230431-1ab0f28a.json) | parts=8, bits=4, nprobe=1, oversample=1 | 0.549 | 8045.4 |
| [faiss-ivfpq](../../../results/runs/tier2-faiss-ivfpq-001-20261104T230432-24898dd7.json) | parts=8, bits=4, nprobe=1, oversample=8 | 0.984 | 7447.6 |
| [faiss-ivfpq](../../../results/runs/tier2-faiss-ivfpq-002-20261104T230434-aa7e2c6b.json) | parts=8, bits=4, nprobe=8, oversample=1 | 0.547 | 7486.1 |
| [faiss-ivfpq](../../../results/runs/tier2-faiss-ivfpq-003-20261104T230436-21ca3a40.json) | parts=8, bits=4, nprobe=8, oversample=8 | 1.000 | 6219.5 |

[Raw lesson observation](lesson-08_quantization-c3fca66c.json)

Qwen prefix comparison on one query, relative to its own full 1024-dimensional ranking:

| Dimensions | Neighbor overlap@10 | Float32 bytes for all 128 documents |
|---:|---:|---:|
| 1024 | 1.0 | 524,288 |
| 512 | 0.9 | 262,144 |
| 256 | 0.9 | 131,072 |
| 64 | 0.8 | 32,768 |
| 32 | 0.8 | 16,384 |

[Central leaderboard](../../../results/leaderboard.md) · [Tier 2 checkpoint analysis](../../../checkpoints/tier2/results/README.md).
