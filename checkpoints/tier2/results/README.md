# Reference checkpoint · choose an index for Marlowe

The development rule chooses the highest measured serial QPS among configurations meeting the family's recall floor, or the highest recall if none qualify. The catalog and deterministic hashing fixture are tuned separately in the final scratch-index run. Hashing tests mechanics. Its scores do not establish semantic quality.

| TinyVec family | Planned fixture floor | Held-out fixture recall | Catalog recall | Catalog parameters |
|---|---:|---:|---:|---|
| lsh | 0.60 | [0.638](../../../results/runs/tier2-lsh-fixture-test-20261104T230942-fcfdfc38.json) | [0.544](../../../results/runs/tier2-lsh-test-20261104T230938-8cb5fa48.json) | `{'kind': 'lsh', 'bits': 5, 'tables': 10}` |
| ivf | 0.85 | [0.996](../../../results/runs/tier2-ivf-fixture-test-20261104T230929-75d60c27.json) | [0.864](../../../results/runs/tier2-ivf-test-20261104T230923-db27c361.json) | `{'kind': 'ivf', 'nlist': 16, 'nprobe': 4}` |
| hnsw | 0.90 | [0.896](../../../results/runs/tier2-hnsw-fixture-test-20261104T230912-cbce568b.json) | [0.874](../../../results/runs/tier2-hnsw-test-20261104T230855-d964b6b3.json) | `{'kind': 'hnsw', 'M': 8, 'efConstruction': 24, 'efSearch': 48}` |
| pq | 0.80 | [0.886](../../../results/runs/tier2-pq-fixture-test-20261104T230956-6db2d402.json) | [0.924](../../../results/runs/tier2-pq-test-20261104T230952-2d0af5fe.json) | `{'kind': 'pq', 'parts': 8, 'centroids': 16, 'oversample': 8}` |

## Native comparisons

| Family / raw held-out run | Recall@10 | nDCG@10 | p50 / p95 ms | Serial QPS ± SD | Index payload bytes |
|---|---:|---:|---:|---:|---:|
| [exact](../../../results/runs/tier2-exact-test-20261104T230422-f02515ab.json) | 1.000 | 0.732 | 1.197 / 1.718 | 790.1 ± 55.6 | — |
| [ivf](../../../results/runs/tier2-ivf-test-20261104T230923-db27c361.json) | 0.864 | 0.847 | 0.161 / 0.429 | 4561.4 ± 667.8 | 28,576 |
| [hnsw](../../../results/runs/tier2-hnsw-test-20261104T230855-d964b6b3.json) | 0.874 | 0.732 | 0.436 / 0.950 | 2052.4 ± 243.2 | 41,308 |
| [pq](../../../results/runs/tier2-pq-test-20261104T230952-2d0af5fe.json) | 0.924 | 0.732 | 0.135 / 0.575 | 4306.9 ± 651.4 | 32,576 |
| [faiss-ivf](../../../results/runs/tier2-faiss-ivf-test-20261104T230429-701b6a91.json) | 0.996 | 0.732 | 0.070 / 0.362 | 7532.0 ± 697.1 | 1,568,843 |
| [faiss-hnsw](../../../results/runs/tier2-faiss-hnsw-test-20261104T230425-df36f06e.json) | 0.996 | 0.732 | 0.067 / 0.357 | 8067.7 ± 139.1 | 1,616,914 |
| [hnswlib](../../../results/runs/tier2-hnswlib-test-20261104T230509-fa08d558.json) | 0.996 | 0.732 | 0.173 / 1.105 | 4433.5 ± 1716.1 | 1,620,920 |
| [usearch](../../../results/runs/tier2-usearch-test-20261104T230555-52fedf88.json) | 0.996 | 0.732 | 0.135 / 0.958 | 4319.2 ± 1504.3 | 1,620,972 |

## Decision

For a 0.90 catalog recall requirement, the measured PQ shortlist reached 0.924. Compare its QPS and p95 with the exact baseline before accepting the extra training and memory cost. Native graph libraries meeting the same floor in this run: faiss-hnsw, hnswlib, usearch.

The teaching graph reached 0.896 against the 0.900 fixture floor. Its connected layer fixes unreachable clusters, but a finite search beam can still stop early. The [earlier proximity-only graph](../../../results/runs/tier2-hnsw-fixture-test-20261104T230505-747688f0.json) achieved 0.414. The graph structure was revised after seeing that miss, so a second test on the same split is a regression check. A fresh query set is needed for an independent estimate.

For strict metadata filters, inspect the [filtered and keyword measurements](../../../modules/10_filtering_hybrid/results/README.md). A graph can traverse ineligible bridges while returning eligible hits. The adaptive alternative scans small eligible sets exactly. For SKU lookups, compare judged relevance, because moving away from the exact dense ranking may be desirable.

Snapshot bytes include original records and rebuild settings. Compressed payload bytes alone omit the cost of storing full vectors for rescoring. The million-vector disk experiment is a separate generated workload with a bounded int8 scan. Its timings cannot rank the catalog ANN engines.

### Selection records

- [decisions-7efed4ca.json](../../../results/tier2/decisions-7efed4ca.json)
- [decisions-81f77e79.json](../../../results/tier2/decisions-81f77e79.json)
- [decisions-a6ef8e7f.json](../../../results/tier2/decisions-a6ef8e7f.json)

### Fixed-budget graph validation

The follow-up fixed a larger graph and beam before running the development split, an original-fixture regression and a new seeded product corpus. Timings are comparable only within matching workload hashes. [Procedure](../../../configs/bench/graph_validation/README.md).

| Raw run | Recall@10 | p95 ms | Logical link bytes |
|---|---:|---:|---:|
| [tier2-graph-budget-development](../../../results/runs/tier2-graph-budget-development-20261104T232802-b64e50ac.json) | 1.000 | 0.676 | 56,096 |
| [tier2-graph-budget-fresh-products](../../../results/runs/tier2-graph-budget-fresh-products-20261104T232805-c75fabc3.json) | 1.000 | 0.703 | 56,096 |
| [tier2-graph-budget-regression](../../../results/runs/tier2-graph-budget-regression-20261104T232804-c4e3827d.json) | 1.000 | 0.706 | 56,096 |
