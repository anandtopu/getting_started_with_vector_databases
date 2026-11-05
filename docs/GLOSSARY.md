# Glossary

118 beginner terms used throughout the course. Definitions describe this repository's contracts; native database terminology may differ. See [cross-database terminology](TERMS_ACROSS_DATABASES.md) and [the mental model](MENTAL_MODEL.md).

**Vector.** An ordered list of numbers representing an item or direction.

**Dimension.** The number of coordinates in a vector; every vector in one collection must match.

**Embedding.** A vector produced by a model to represent text, images or another input.

**Embedding space.** The coordinate system defined by a particular model and preprocessing recipe.

**Model revision.** An immutable model version used to make repeated embedding runs comparable.

**Normalization.** Rescaling a vector, often to unit length.

**Norm.** A measure of vector length; the L2 norm is the square root of the sum of squared coordinates.

**Dot product.** The sum of coordinate-wise products; higher values can indicate stronger alignment.

**Cosine similarity.** Dot product divided by both vector norms; undefined for a zero vector.

**Euclidean distance.** Straight-line L2 distance between two vectors.

**Squared L2.** The sum of squared coordinate differences; it preserves the ordering of L2 distances.

**Metric.** A distance rule; in practice API metric names may also include similarity scores.

**Float32.** A 32-bit floating-point representation using four bytes per value.

**Float16.** A two-byte floating-point representation that can change distances through rounding.

**Dtype.** The numeric storage type of an array.

**Zero vector.** A vector with all coordinates zero; reject it for cosine search.

**NaN.** A nonnumeric floating-point value that must not enter distance calculations.

**Infinity.** An unbounded floating-point value; vector validation rejects it.

**Nearest neighbor.** An item closest to a query under the chosen distance.

**k.** The requested number of neighbors.

**Exact search.** Examining all eligible vectors to obtain the true nearest neighbors under the implemented metric.

**ANN.** Approximate nearest-neighbor search, which trades possible misses for resource savings.

**Index.** An auxiliary data structure that makes retrieval more efficient.

**Candidate.** An item considered by an approximate index before the final result selection.

**Oversampling.** Retrieving more candidates than the final k so filtering or rescoring has room to work.

**Rescoring.** Recomputing candidate distances, often from retained full-precision vectors.

**Reranking.** Applying another relevance model or rule to an existing candidate list.

**LSH.** Locality-sensitive hashing: related vectors are likely to share a bucket.

**Hash table.** A structure mapping a key or hash to stored items.

**IVF.** An inverted-file index that groups vectors by coarse centroids.

**Centroid.** A representative center of a vector cluster.

**nlist.** The number of coarse partitions in an IVF index.

**nprobe.** The number of IVF partitions visited by a query.

**HNSW.** A multilayer neighbor graph used for approximate retrieval.

**M.** A graph connectivity parameter; its exact interpretation depends on the implementation.

**efConstruction.** The search effort used while constructing an HNSW graph.

**efSearch.** The candidate exploration effort used during an HNSW query.

**Quantization.** Representing numeric values with a smaller set of possible values.

**Scalar quantization.** Compressing individual coordinates, for example from float32 to int8.

**Binary quantization.** Representing a coordinate or projection using a bit.

**Product quantization.** Splitting vectors into subspaces and encoding each subvector with a learned codebook entry.

**Codebook.** A set of representative vectors used to encode and reconstruct values.

**Residual.** The difference between a vector and its approximation or coarse center.

**RaBitQ.** A randomized quantization method with a distance estimator; the course implements its core educational form.

**Random rotation.** A seeded change of basis preserving distances when the matrix is orthogonal.

**Disk index.** An index whose retrieval reads some data from persistent storage rather than keeping everything in RAM.

**Memory map.** A file-backed array view whose pages are loaded by the operating system.

**Page cache.** Operating-system memory holding recently accessed file pages.

**Collection.** A logical group of vector records with a defined schema or vector configuration.

**Record.** An ID, vector and associated metadata/text in the shared course contract.

**Payload.** Database terminology for nonvector fields attached to a vector record.

**Metadata.** Structured attributes such as seller, price and availability.

**Schema.** Rules describing fields, types and required structure.

**Upsert.** Insert a new ID or replace/update an existing ID according to the database contract.

**Tombstone.** A marker identifying a deleted record until storage/index cleanup occurs.

**Filter.** A condition determining which records are eligible.

**Prefilter.** Apply eligibility before nearest-neighbor candidate selection.

**Postfilter.** Filter already selected candidates, potentially returning fewer than k.

**Selectivity.** The fraction of records satisfying a filter.

**Tenant.** A customer or organizational boundary whose private data must be isolated.

**Tenant isolation.** Preventing one tenant from reading or changing another tenant's private data.

**RBAC.** Role-based access control, such as reader and administrator permissions.

**Authentication.** Establishing who a caller is.

**Authorization.** Deciding which operations that identity may perform.

**TLS.** Transport encryption with certificate-based server verification.

**Certificate authority.** A trusted signer used to verify a server certificate.

**Secret.** A credential such as a bearer token or private key that must not enter public artifacts.

**WAL.** A write-ahead log persisted before acknowledging a mutation.

**fsync.** A request to flush file data to durable storage; guarantees depend on the OS and hardware.

**Checkpoint.** A saved state plus a log position from which replay can resume.

**Replay.** Reapplying recorded operations after restart.

**Checksum.** A digest used to detect changed bytes; it does not establish who created them.

**Atomic replace.** Publishing a completed file by replacing a path in one filesystem operation.

**Idempotence.** Repeating an operation has the same intended final effect as applying it once.

**Snapshot.** A point-in-time copy used for restore or inspection.

**Backup.** A retained copy plus enough procedure and metadata to restore the intended state.

**RPO.** Recovery point objective: the acceptable amount of data that may be lost.

**RTO.** Recovery time objective: the acceptable time to restore service.

**Replication.** Maintaining copies across nodes for durability or availability.

**Shard.** A partition of data assigned to part of a distributed system.

**Read consistency.** The rule determining which replicas must agree or respond to a read.

**Alias.** A stable logical name that can point to a different collection during migration.

**Blue-green migration.** Preparing a new collection alongside the old one, validating it, then switching an alias.

**Ground truth.** Reference answers used to judge a retrieval experiment.

**Recall@k.** The fraction of eligible exact or judged relevant items recovered, under a stated denominator.

**Precision@k.** The fraction of returned items that are judged relevant.

**MRR.** Mean reciprocal rank of the first relevant result.

**nDCG.** A rank-discounted relevance measure normalized by the best possible ranking.

**Qrels.** Query-relevance judgments linking query IDs to graded document relevance.

**Tie tolerance.** An explicit distance boundary allowance for numerically equivalent neighbors.

**Development split.** Queries used to select settings.

**Held-out split.** Queries reserved for evaluating the selected settings.

**Data leakage.** Using evaluation information during tuning in a way that overstates generalization.

**Warmup.** Unmeasured requests used to stabilize initialization or cache state before timing.

**Latency.** Elapsed time for one operation; its start and end boundaries must be stated.

**p95.** The 95th percentile: 95 percent of observed values are at or below this value.

**Throughput.** Completed operations divided by elapsed wall time.

**Concurrency.** The number of overlapping operations; it is not the same as CPU parallelism.

**RSS.** Resident memory attributed to a process; client RSS does not measure a separate server.

**Provenance.** The versions, inputs, commands and environment explaining where an artifact came from.

**BM25.** A lexical relevance score based on term occurrence, rarity and document length.

**Sparse vector.** A vector represented mainly by its nonzero coordinates.

**Hybrid search.** Combining lexical/sparse and dense retrieval signals.

**RRF.** Reciprocal rank fusion: combine ranked lists using reciprocal rank contributions.

**Cross-encoder.** A model that scores a query and candidate together, commonly used for reranking.

**Late interaction.** Comparing token-level query and document representations after separate encoding.

**MaxSim.** For each query token, take its best document-token similarity, then aggregate.

**Chunk.** A passage cut from a larger document for retrieval.

**RAG.** Retrieval-augmented generation: supply retrieved evidence to a generator.

**Citation validity.** Whether a cited identifier exists in the allowed evidence set.

**Faithfulness.** Whether the answer's claims are supported by the retrieved evidence.

**Abstention.** Declining to answer when evidence is insufficient.

**Prompt injection.** Untrusted input attempting to redirect a model's instructions.

**Multimodal.** Using more than one data modality, such as text and images.

**Cold start.** A recommendation case with little or no interaction history.

**Deduplication.** Identifying repeated or near-identical items under a defined threshold.

**Drift.** A change in data or model behavior that may invalidate earlier evaluation.

**SLO.** A measurable service-level objective, such as a latency target with a defined error budget.
