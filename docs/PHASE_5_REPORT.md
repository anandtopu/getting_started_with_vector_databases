# Phase 5 · real database lessons and comparison

Tier 3 delivers Modules 11–16, eleven new database adapters and a common workload measured on twelve databases. The six lessons contain 37 examples, six use cases, 18 runnable exercises with reference solutions, 36 quiz questions and six notebooks. Begin with the embedded lesson and finish with the database-selection checkpoint. [Module 11](../modules/11_embedded/README.md) · [Tier 3 checkpoint](../checkpoints/tier3/README.md).

| Lesson | Native work exercised | Results |
|---|---|---|
| Embedded databases | Chroma reopen/update/filter, Lance table versions and IVF-PQ, SQLite distances, DuckDB exact and VSS HNSW | [Module 11](../modules/11_embedded/results/README.md) |
| PostgreSQL | Vector, halfvec and bit operators, joins, rollback, HNSW/IVFFlat, full-text fusion and archive restore | [Module 12](../modules/12_pgvector/results/README.md) |
| Qdrant | Payload indexing, quantized search, named dense/sparse fields, MaxSim, seller scope and native snapshot restore | [Module 13](../modules/13_qdrant/results/README.md) |
| Weaviate | V4 collection API, alpha sweep, tenants, filesystem backup restore and local generative query | [Module 14](../modules/14_weaviate/results/README.md) |
| Milvus | Explicit schemas, IVF/HNSW, BM25 fusion, partition keys, read visibility and fully built DISKANN | [Module 15](../modules/15_milvus/results/README.md) |
| Wider landscape | Elasticsearch, Redis, Atlas Local, Vespa, FAISS over HTTP and a local managed-cost exercise | [Module 16](../modules/16_landscape/results/README.md) |

## What the comparison showed

The matched workload used 500 included MiniLM product vectors and 50 held-out queries, with twenty warm-ups and five repetitions. Chroma, LanceDB, SQLite-vec, DuckDB, PostgreSQL, Qdrant, Weaviate, Milvus, Redis, Atlas Local and Vespa each reached 1.000 eligible-neighbor recall@10. The initial Elasticsearch approximate configuration reached 0.854. The reference recommendation combines a recall floor and latency budget with the application’s storage and operating requirements. [Raw runs, chart and recommendation](../checkpoints/tier3/results/README.md).

The portable comparison evaluates the shared typed predicate in a session metadata catalog, then supplies eligible IDs to the native query. The adapters also store a packed payload for logical export. These choices preserve one predicate contract and make cross-database restore verifiable. They add overhead and storage that must be included when interpreting the rows. Native examples separately test engine-specific field filtering, ranking and backup APIs.

## Verified recovery and readiness

The common lifecycle contract exercised writes, updates, strict filters, deletion and logical restoration through all eleven new adapters. Native Qdrant snapshots and Weaviate filesystem backups restored their query results. A PostgreSQL archive created by pg_dump restored the nearest item in a different temporary database.

Milvus initially reported a finished index with zero indexed rows. The disk lesson now waits until indexed_rows reaches 4,096 and pending_index_rows is zero before refreshing the loaded index and searching. The consistency experiment also observed an empty Eventually read immediately after insertion, followed by visible Session and Strong reads. [Milvus observations](../modules/15_milvus/results/README.md).

Atlas Local search visibility is checked using a new revision marker on each written batch. After deletion the adapter restricts retrieval to live session keys. Weaviate connections skip the client’s public package-update check and explicitly verify local readiness, allowing offline tests to keep external sockets blocked.

The optional local generative query retrieved the title “Coral ceramic mug warmer” and returned that title through Weaviate and Ollama. It used the previously pinned Qwen model and a short caption preset with bounded CPU threads and output. Its model identity is in the runtime evidence. [Generation observation](../modules/14_weaviate/results/README.md) · [Runtime identities](../research/phase5-local-runtime.json).

## Validation and limits

The installed-environment default suite passed **212 tests**, with eleven opt-in server/live tests outside the default selection. The base-only environment passed **156 tests**, with 56 optional-library checks skipped. A separate live run passed all **eleven new adapter contracts**. The final Tier 3 script record contains **43 passes, zero failures and zero skips**. All **seventeen notebooks and 112 code cells** executed, including the six new notebooks and all their enabled native database cells. [Script execution](../results/tier3/execution-df533956.json) · [Verification record](../research/phase5-validation.json).

A failed native batch may have partially applied. The session now blocks later reads, writes and snapshot publication after such a failure, while still allowing its private collection to be closed. A regression test verifies this behavior.

The development machine’s default Docker Desktop connection was unavailable, and its rootful Podman bridge still failed while applying nftables rules. We used isolated rootless Podman containers with pasta networking and loopback-only published ports. Milvus dependencies shared a private pod. PostgreSQL used local port 15432 for verification. The published Compose file retains the portable service topology and default ports. Its structure was checked, and its pinned database images were executed through that documented local alternative.

The Windows client and Linux VM share one physical machine. Python RSS covers the client. Container memory evidence is a post-run sample rather than a per-request peak. Hosted CI, macOS runtime behavior and production concurrency remain unverified. The CI workflow now defines separate server jobs for the new adapter contracts.

The optional pgvectorscale extension was absent from the pinned pgvector image, so its example reports availability and makes no index-performance claim. Managed service pricing and cleanup are documented, and the worksheet runs locally. No managed account or paid resource was created. Tier 4 application work belongs to Phase 6.

The isolated rootless test pods and containers were removed after verification. The failed rootful verification project's container, network and volume were also removed. Downloaded image caches remain available. [Cleanup record](../research/phase5-cleanup.json).
