# Tier 2 vocabulary

| Term | Meaning in this course |
|---|---|
| Candidate | A row the first retrieval stage permits the final scorer to consider. |
| ANN | Approximate nearest neighbors. Faster or smaller retrieval may miss true neighbors. |
| LSH | Locality-sensitive hashing gives nearby vectors a chance to share a bucket. |
| Hyperplane | A flat boundary separating the positive and negative sides of a dot product. |
| K-means | Repeatedly assign rows to nearest centers, then average each center's members. |
| IVF | An inverted file maps centers to lists of assigned product IDs. |
| nlist / nprobe | How many coarse lists exist / how many a query visits. |
| Beam | A bounded set of promising search alternatives. |
| HNSW | Hierarchical navigable small world graph. Sparse upper layers guide a search into a denser bottom layer. |
| M / efConstruction / efSearch | Bound on links / construction candidate budget / query candidate budget. |
| Tombstone | A deletion marker that excludes an item while its graph links may remain useful. |
| Quantization | Replace many possible float values with fewer codes. |
| Codebook / residual | Learned representative values / the difference between a row and its coarse center. |
| Rescoring | Evaluate the original vectors or a richer scorer on retrieved candidates. |
| Matryoshka | Training that encourages shorter prefixes of one embedding to remain useful. |
| Memory map | A file whose pages the OS can make available as memory. |
| Vamana | A pruned proximity graph used in DiskANN designs. |
| Posting | A list of document IDs sharing a term or metadata value. |
| BM25 | A lexical scoring rule using term rarity, frequency and document length. |
| RRF | Reciprocal rank fusion combines lists using rank positions. |
| MaxSim | Each query token contributes its best similarity to any document token. |
| Cross-encoder | A model that reads query and candidate jointly to produce one relevance score. |

[Review Tier 1 vocabulary](TIER1_TERMS.md).
