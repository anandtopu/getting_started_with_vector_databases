# Shared foundation

Tier 3 adds Chroma, LanceDB, DuckDB, PostgreSQL, Qdrant, Weaviate, Milvus, Elasticsearch, Redis, Atlas Local and Vespa through the same registry. The common database lifecycle owns a private collection, validates cosine-space identity, pushes eligible IDs into native retrieval and exports rows read back from the engine. Session close removes only that run's collection. [Adapter lifecycle](stores/database.py) · [Database comparison](../checkpoints/tier3/results/README.md).

The `ann` registry backend adds indexed TinyVec to the exact engines below. Choose its candidate generator with `kind`, for example `make_store("ann", kind="ivf", nlist=16, nprobe=4)`. It supports cosine vectors, portable metadata filters, application-side hybrid retrieval and snapshots that rebuild indexes on reload. [Implementation](stores/ann.py) · [Tier 2 benchmark decisions](../checkpoints/tier2/results/README.md).

`stores.protocol.VectorStore` describes collection creation, upsert, delete, search, explicit hybrid search, snapshot saving, and close. Implemented engines are registered in `stores.registry`: TinyVec, SQLite-vec, and FAISS flat. The FAISS adapter uses TinyVec records/snapshots plus exact native scoring; filtered calls build a temporary eligible index and all scores are retrieved for deterministic ties. Unsupported hybrid search raises a clear error and capabilities advertise `hybrid="none"`. TinyVec also supports insert-only batches that reject conflicting IDs before any mutation.

Records contain a string ID, finite vector, JSON metadata, and optional text. A collection fixes dimensions, distance metric, and embedding-space identity. Portable scores are higher-is-better: cosine similarity, dot product, or negative Euclidean distance. Native scores are retained when available. Cosine zero vectors are rejected. Search ties use string ID order. Applications always pass the embedding-space identity.

Filters accept `eq`, `in`, numeric `lt/lte/gt/gte`, and nested `and/or`. Comparison values are finite JSON scalars. Equality preserves JSON scalar types; a boolean is not the number one. Missing keys never satisfy a comparison, including equality with null. Numeric ranges compare integers/floats. SQLite uses bound parameters; the same contract tests cover both engines. Filters are a retrieval mechanism, not an authorization system: a trusted application must enforce tenant constraints.

`embeddings.py` provides deterministic test hashing, lazy CPU MiniLM, SigLIP helpers, and content/revision/role/preprocessing-addressed caches. Real and test embedding spaces are distinct. `llm.py` provides explicit local Ollama calls and manifest checking without pulling weights. `generation.py` owns deterministic synthetic data and attribute-derived judgments. `bench/` owns workloads, timing, ground truth, metrics, memory sampling, sweeps, reports, and plots.

Model inference is optional. Core examples read real precomputed vectors without loading model packages. Image inference and generation helpers await their later end-to-end evaluation; their availability is not a quality claim.


Tier 4 adds `apps/marlowe.py` as the shared v5 application, with filtered hybrid search, scoped RAG and source-excerpt delivery, time-bounded recommendations, duplicate calibration, review themes and named image/text search. `search/query_parser.py` owns conservative constraint parsing. [Application architecture and setup](../docs/TIER4_APPLICATIONS.md).

Tier 5 adds `ops/` for bounded ingestion, caching, migrations, capacity and backup/restore, and `security/` for trusted identity, deletion history, local TLS and minimized audit. `apps/secure_market.py` and `apps/secure_api.py` wrap all private v5 flows in seller scope. [v6 runbook](../docs/TIER5_RUNBOOK.md).
