# Reading list

Read the mechanism before copying a benchmark headline. For every paper, write down its dataset, metric, quality target, hardware, memory accounting and timing boundary, then compare those choices with this course. Links were checked during the build; publisher access restrictions are recorded in the final audit.

## Locality-sensitive hashing

[Indyk and Motwani, Approximate Nearest Neighbors (1998)](https://doi.org/10.1145/276698.276876) develops randomized indexing for approximate proximity search in high dimensions. The useful lesson is that hash collisions can be designed to favor nearby points, while table count and collision selectivity create a resource/quality trade-off; Module 05 implements a small random-hyperplane variant rather than the entire theoretical construction.

## IVF and product quantization

[Jegou, Douze and Schmid, Product Quantization for Nearest Neighbor Search (2011)](https://doi.org/10.1109/TPAMI.2010.57) encodes subvectors with separate learned codebooks so that distances can be estimated from compact codes. It also combines coarse partitioning with compressed residuals; compare the course's separate IVF and PQ implementations before studying the combined structure.

[FAISS index guide](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes) is the implementation companion for flat, inverted-file, graph and compressed indexes. Use its storage formulas to check what an index retains, and distinguish code bytes from total memory including IDs, codebooks and full vectors used for rescoring.

## Navigable graphs

[Malkov and Yashunin, HNSW](https://arxiv.org/abs/1603.09320) organizes neighbor links into a hierarchy so queries can move from coarse navigation to local refinement. Its graph construction and exploration budgets explain why M, efConstruction and efSearch affect different costs; the course implementation deliberately exposes these mechanics and is not a performance clone.

## Disk-based search

[Subramanya et al., DiskANN](https://www.microsoft.com/en-us/research/publication/diskann-fast-accurate-billion-point-nearest-neighbor-search-on-a-single-node/) combines graph search with a storage design that allows a much larger corpus than a fully resident graph. Focus on what stays in memory, what requires disk reads, and how cache and I/O concurrency affect the latency claim; the laptop exercises measure smaller systems with different hardware.

## Quantization objectives and recent methods

[Guo et al., Accelerating Large-Scale Inference with Anisotropic Vector Quantization](https://arxiv.org/abs/1908.10396) changes the compression objective to emphasize errors that matter for maximum-inner-product retrieval. It is a reminder that low reconstruction error and good ranking are different goals; compare that distinction with the course's simple PQ training objective.

[Gao and Long, RaBitQ](https://arxiv.org/abs/2405.12497) uses randomized quantization and a corrected distance estimator with theoretical error analysis. B4 reconstructs the core rotation/sign estimator and measures installed FAISS one-bit and four-bit variants, while explicitly omitting the paper's optimized SIMD/pruning implementation and full-scale evaluation.

## Text representations and late interaction

[Reimers and Gurevych, Sentence-BERT](https://arxiv.org/abs/1908.10084) makes independent sentence representations useful for similarity comparisons without encoding every candidate together with the query. Read it to understand why precomputed embeddings make retrieval feasible, then inspect the exact model revision and preprocessing used by this course.

[Khattab and Zaharia, ColBERT](https://arxiv.org/abs/2004.12832) preserves token-level representations and delays their interaction until scoring. Its approach offers more detailed matching than one vector per passage at additional storage and scoring cost; the course's MaxSim lesson demonstrates the operation rather than training ColBERT.

## Fusion and generation

[Cormack, Clarke and Buettcher, Reciprocal Rank Fusion](https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/) combines ranked lists through reciprocal rank contributions instead of assuming their raw scores share a scale. This is the basis for the course's lexical/dense and multimodal fusion exercises, where candidate coverage still limits the final ranking.

[Lewis et al., Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401) combines a retriever's external evidence with a generator's learned language model. The paper motivates separating parametric knowledge from accessible documents; in the course, retrieval quality, citation validity and claim support remain separate evaluation questions.

## Reproducible benchmarks

[ANN-Benchmarks](https://github.com/erikbern/ann-benchmarks) provides a shared framework for comparing approximate-neighbor implementations across datasets and settings. Study how the quality/throughput curve changes with query effort, and never transfer a plotted result to another corpus or machine without rerunning the experiment.

[Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist) supplies labeled clothing images and documented dataset provenance. B3 uses a checksummed subset of raw pixel vectors to reproduce a small recall/effort relationship; image classification labels and vector-neighbor ground truth answer different questions.
