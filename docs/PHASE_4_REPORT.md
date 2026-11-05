# Phase 4 · Tier 2 indexing and hybrid search

Modules 05–10 extend the exact store into a search engine learners can tune, compress and compare with native libraries. The core lessons run locally with included embeddings. Start with [Module 05](../modules/05_ann_lsh/README.md) and finish with the [checkpoint and reference analysis](../checkpoints/tier2/README.md).

| Lesson | What runs | Evidence |
|---|---|---|
| [05 · Approximate neighbors](../modules/05_ann_lsh/README.md) | Random-plane hash buckets, candidate coverage and FAISS binary-code search | [LSH results](../modules/05_ann_lsh/results/README.md) |
| [06 · IVF](../modules/06_ivf/README.md) | Seeded k-means training, inverted lists, nprobe sweep and FAISS IVFFlat | [IVF results](../modules/06_ivf/results/README.md) |
| [07 · HNSW](../modules/07_hnsw/README.md) | Multilayer graph, construction and query beams, retirement, FAISS, USearch and hnswlib | [Graph results](../modules/07_hnsw/results/README.md) |
| [08 · Compression](../modules/08_quantization/README.md) | Int8, packed bits, PQ, native IVF-PQ, full-vector rescoring and real Qwen prefix retrieval | [Quality and memory](../modules/08_quantization/results/README.md) |
| [09 · Disk scale](../modules/09_disk_scale/README.md) | Million-row mapped scan, bounded on-disk graph reads and USearch mapped graph restore | [Disk and page-read measurements](../modules/09_disk_scale/results/README.md) |
| [10 · Hybrid retrieval](../modules/10_filtering_hybrid/README.md) | Metadata postings, graph-aware filtering, BM25, RRF, token MaxSim, LanceDB and cross-encoder reranking | [Filtered and lexical results](../modules/10_filtering_hybrid/results/README.md) |

## Results that affect the decision

On the planned hashing fixture, held-out recall@10 was **0.638 for LSH**, **0.996 for IVF**, **0.896 for simplified HNSW** and **0.886 for rescored PQ**. Three of the four met their preset targets. HNSW fell 0.004 short of its 0.900 floor. A graph built only from proximity links had scored 0.414. The revision retains diverse neighbors and a bounded insertion-order ring that connects each layer. The same test split was revisited after the structural change, so a fresh evaluation set would be needed for an independent generalization claim. [Raw selections and both graph runs](../checkpoints/tier2/results/README.md).

On the separate held-out MiniLM catalog workload, scratch PQ reached 0.924 recall and FAISS HNSW, USearch and hnswlib each reached 0.996. On the filtered/keyword workload, postfiltering reached 0.630 recall and graph traversal through ineligible nodes reached 0.785. Adaptive filtering also reached 0.785. The boots use case returned five northern, in-stock waterproof hiking boots costing less than $100. [Catalog comparison](../checkpoints/tier2/results/README.md) · [Filter results](../modules/10_filtering_hybrid/results/README.md).

The million-vector experiment generated 32-dimensional unit vectors in bounded blocks, computed independent float truth, then searched the int8 file. The file used **32,000,128 bytes** and mean recall@10 was **0.980** across five queries. File size includes a header. Scan timings depend on the OS page cache. The separate graph-page experiment made actual local reads and modeled the bytes that different remote fragment sizes would require. [Raw evidence and memory measurements](../modules/09_disk_scale/results/README.md).

## What was verified

For a graph configuration selected for accuracy, we fixed M=12, efConstruction=64 and efSearch=96 before running a separate validation. Recall@10 reached **1.000 on both the original fixture and a fresh seeded product corpus**. On the matched original fixture, the graph link payload grew from 41,308 to 56,096 bytes and p95 retrieval time increased from 0.499 to 0.706 ms. This option met the 0.900 floor at a measurable cost. The corpus draw reuses the synthetic query templates. [Budget and procedure](../configs/bench/graph_validation/README.md) · [Original fixture](../results/runs/tier2-graph-budget-regression-20261104T232804-c4e3827d.json) · [Fresh fixture](../results/runs/tier2-graph-budget-fresh-products-20261104T232805-c75fabc3.json).

The six modules add 25 example scripts, six product use cases, 18 runnable exercise starters and solutions, six notebooks and 36 quiz questions. The learner can change graph parameters in the Playground and inspect actual links. Indexed TinyVec preserves records and index settings in a checksummed snapshot, then rebuilds the candidate index on reload. The benchmark harness runs the same eligible-neighbor reference for native and teaching indexes. Its feature profiles link whole-script observations separately from repeated retrieval timings. [Leaderboard](../results/leaderboard.md) · [Feature map](FEATURE_MAP.md).

Local verification used Windows 11 and Python 3.12.13. The installed-environment suite includes graph reachability, mutation and restore, PQ lookup, filtered traversal, real native indexes and a Streamlit interaction. The examples and notebooks ran offline after installation. The Qwen and cross-encoder weights were downloaded once to prepare small, checksummed samples. The graph native comparisons included the locally compiled optional hnswlib. [Model sample](../data/tier2/README.md) · [Setup and commands](SETUP.md).

The machine reported 24 cores and 31.46 GiB RAM. Timings describe serial retrieval on that machine. Raw results retain a source hash, installed package versions and hardware. Hosted CI, macOS, cold SSD reads, actual object storage and a deployed DiskANN server remain outside the local evidence. Tier 3 server lessons begin in Phase 5.

The final Windows verification passed 171 tests, all 55 example and use-case scripts, and all 63 code cells across eleven notebooks. The default test selection leaves three opt-in live or container tests out. All 114 included data artifacts passed checksum verification. The checker also verified the eleven lesson structures, local links and Markdown anchors.
