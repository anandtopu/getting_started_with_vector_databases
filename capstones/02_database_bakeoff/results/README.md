# Reference measurements

500 included MiniLM vectors, 30 test queries, k=10, three repetitions and five warmups. These are small local observations; source/config/hardware are in each raw record.

| Configuration | Recall@10 | p95 ms | Errors | Evidence |
|---|---:|---:|---:|---|
| capstone-bakeoff-chroma | 1.000 | 1.575 | 0 | [raw](../../../results/runs/capstone-bakeoff-chroma-20261105T200607-e380b2ea.json) |
| capstone-bakeoff-lancedb | 1.000 | 8.099 | 0 | [raw](../../../results/runs/capstone-bakeoff-lancedb-20261105T200616-b9d21e65.json) |
| capstone-bakeoff-sqlite-vec | 1.000 | 0.595 | 0 | [raw](../../../results/runs/capstone-bakeoff-sqlite-vec-20261105T200550-7c08ae00.json) |

Retained vectors, build cost and memory are in the raw reports. Do not infer scale or concurrent service performance from these numbers. [Full interpretation](../../../docs/PHASE_8_REPORT.md).
