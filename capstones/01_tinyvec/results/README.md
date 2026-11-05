# Reference measurements

500 included MiniLM vectors, 30 test queries, k=10, three repetitions and five warmups. These are small local observations; source/config/hardware are in each raw record.

| Configuration | Recall@10 | p95 ms | Errors | Evidence |
|---|---:|---:|---:|---|
| capstone-tinyvec-faiss-flat | 1.000 | 0.957 | 0 | [raw](../../../results/runs/capstone-tinyvec-faiss-flat-20261105T200543-2e100b2d.json) |
| capstone-tinyvec-hnsw | 1.000 | 0.979 | 0 | [raw](../../../results/runs/capstone-tinyvec-hnsw-20261105T200538-2b2383fb.json) |
| capstone-tinyvec-pq | 1.000 | 0.323 | 0 | [raw](../../../results/runs/capstone-tinyvec-pq-20261105T200541-84fea829.json) |

Retained vectors, build cost and memory are in the raw reports. Do not infer scale or concurrent service performance from these numbers. [Full interpretation](../../../docs/PHASE_8_REPORT.md).
