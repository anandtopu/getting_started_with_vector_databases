# Index tuning guide

Optimize a measured constraint: recall, tail latency, resident memory, disk cost or update freshness. Keep metric, model, dtype, eligible filter set and query split fixed while changing one control. Index recall measures agreement with exact neighbors; it does not measure whether the neighbors answer the user's question.

## A repeatable loop

1. Compute exact ground truth on the stored vectors, including any float16 rounding and filters.
2. Reserve development and held-out queries. Record corpus/query checksums and thread counts.
3. Choose a recall floor and a latency/memory budget before looking at results.
4. Sweep query effort first, then rebuild controls if no point qualifies.
5. Evaluate the selected setting once on held-out data. Report failures and uncertainty.
6. Repeat selective-filter and update/deletion cases; rehearse persistence and rebuilds.

## Controls and starting experiments

| Index | Build control | Query control | What to observe |
|---|---|---|---|
| Exact flat | dtype, contiguous storage | batch size, thread count | Linear work; a strong small-corpus baseline |
| LSH | number of tables and hash bits | probes / candidate cap | More tables cost memory; narrow buckets can miss neighbors |
| IVF | number of lists, training sample | nprobe | More probes inspect more partitions; empty/imbalanced lists reveal poor training |
| HNSW | M, efConstruction | efSearch, at least k | More graph links/build effort can improve recall at memory/build cost |
| Scalar / binary | precision, scale/threshold calibration | candidate oversampling, rescore | Count full-vector retention and calibration drift |
| PQ | subspaces, codebook size, training set | approximate candidates and rescore budget | Compression error, divisibility and codebook overhead |
| Disk graph | graph/build settings and cache | beam/search budget | Actual disk reads, cache warmth and I/O tail latency |
| RaBitQ | seed/rotation, bit depth | candidates for exact rescore | Quantized estimator error and total memory including rotation/full vectors |

These controls describe the mechanisms; spelling and semantics vary by backend. [FAISS index documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes) gives its supported families and storage accounting.

## Tested course settings, not universal defaults

The original small hashing fixture reached recall@10 of 0.638 (LSH), 0.996 (IVF), 0.896 (scratch HNSW) and 0.886 (rescored PQ). The initial HNSW setting missed the 0.900 target. A later M=12, efConstruction=64, efSearch=96 validation reached 1.000 on the original and a fresh seeded synthetic corpus, with greater link memory and latency. The query templates were reused, so that is not independent domain validation. [Full measurements](PHASE_4_REPORT.md).

Capstone 01 uses 500 catalog vectors, HNSW M=12/efSearch=80 and PQ with 16 subspaces, 16 centroids and 32x candidate oversampling; both reached recall 1.000 in the recorded small comparison. Retaining and rescoring full vectors contributes to that result. [Runnable comparison](../capstones/01_tinyvec/README.md).

B3 selects FAISS HNSW query effort on 60 Fashion-MNIST queries and tests 60 held-out queries over 3,000 pixel vectors. The recorded efSearch=10 selection reached 0.97 boundary-aware recall@10. It is a small mechanism reproduction, not a reproduction of a paper's full performance table. [Research lesson](../modules/bonus/B3_research_benchmarks/README.md).

## Database controls

| System | Query tuning surface | Operational check |
|---|---|---|
| pgvector | hnsw.ef_search or ivfflat.probes; iterative scans where supported | Use EXPLAIN and test selective filters on the pinned extension |
| Qdrant | SearchParams.hnsw_ef, exact search, quantization/rescore controls | Verify payload indexing and readiness before measuring |
| Weaviate | ef or dynamicEf controls and filter strategy | Keep construction settings distinct from query settings |
| FAISS | index.hnsw.efSearch, index.nprobe | Set CPU threads explicitly; time Python and kernel scopes separately |
| SQLite-vec | Exact query/filter plan in this course | Do not invent an efSearch control for an exact path |
| LanceDB | nprobes/refine factor for relevant indexes | Confirm an index exists and has been trained before labeling a run ANN |

See [pgvector](https://github.com/pgvector/pgvector), [Weaviate vector-index controls](https://docs.weaviate.io/weaviate/config-refs/indexing/vector-index), [Qdrant client lesson](../modules/13_qdrant/README.md), and [LanceDB search](https://docs.lancedb.com/search/vector-search). Course scripts use the pinned API; check the installed client signature before copying settings from newer documentation.

## When recall is unexpectedly low

Check the vector space and normalization first, then eligible-set truth and tie handling. Inspect whether filtering occurs before candidate generation or after it: a fast global top-k followed by a selective filter can return too few eligible neighbors. Increase candidate effort only after these contracts are correct. A new embedding model requires a separate collection/index, backfill, validation and alias switch; changing dimension alone does not define compatibility.

## When latency is unexpectedly high

Separate cold startup, embedding, build/readiness, network, retrieval, reranking and generation. Disable accidental thread oversubscription. Report warmup, query count, repetitions and errors alongside percentiles. Small samples produce unstable p99 estimates; measure realistic concurrency separately from serialized QPS. Saturation and restart failures from the [operations report](PHASE_7_REPORT.md) remain part of the result.
