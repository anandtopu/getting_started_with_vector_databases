# Terms across databases

A vector search system needs a place to group records, a stable record ID, fields that describe each record, and a way to search those fields. The names differ.

| System | Group of records | Record | Descriptive fields | Vector representation | Search structure |
|---|---|---|---|---|---|
| TinyVec | Collection | Record | Metadata dictionary | NumPy vector | Exact scan or a Tier 2 candidate index |
| Chroma | Collection | ID with embedding and document | Metadata | Embedding | HNSW collection configuration |
| LanceDB | Table | Arrow row | Typed columns | Fixed-size list column | Vector and full-text indexes |
| SQLite-vec | SQL table or vec0 virtual table | Row | SQL columns or metadata fields | Vector value | Scalar scan or vec0 retrieval |
| DuckDB | Table | Row | SQL columns | Fixed-size ARRAY | Exact expression or VSS HNSW |
| PostgreSQL | Table | Row with primary key | SQL columns and joined tables | vector, halfvec or bit | HNSW, IVFFlat, full-text GIN |
| Qdrant | Collection | Point | Payload | Named dense, sparse or multivectors | HNSW and payload indexes |
| Weaviate | Collection | Object with UUID | Properties | Self-provided or configured vectors | Vector and inverted indexes |
| Milvus | Collection | Entity with primary key | Scalar fields | Dense and sparse vector fields | Index per vector field and scalar indexes |
| Elasticsearch | Index | Document with ID | Mapped fields | dense_vector | Lucene vector and inverted indexes |
| Redis Search | Search index over hashes or JSON | Redis key | Hash fields or JSON paths | Binary vector field | FLAT or HNSW plus text/tag indexes |
| Atlas Local | Collection | BSON document | BSON fields | Array of numbers | Separate vector search index |
| Vespa | Document type in an application | Document ID | Schema fields | Tensor field | Attribute, inverted and HNSW structures |
| FAISS service | Application-owned collection | Application-owned ID | Application-owned record | FAISS vector | Selected FAISS index |

An index in Elasticsearch groups documents, whereas an index in PostgreSQL or LanceDB usually accelerates a particular table operation. A Milvus partition is a subdivision of a collection. A Weaviate tenant identifies a separate tenant context within a collection. A Qdrant payload condition is a filter and must be derived from trusted application context before it can enforce a tenant restriction.

A **logical export** reads records and writes them in a portable format. Reimport rebuilds the database structures. A **native backup** also preserves database-specific state according to the engine’s backup contract. Test restoration into a separate resource and repeat a known query.

A **readiness check** confirms that the expected service can answer. An **index readiness check** confirms that searchable data or index coverage has reached the required state. The Atlas Local write check uses a revision marker. The Milvus disk experiment requires all 4,096 sealed rows to appear in indexed_rows.

The course’s portable comparison supports cosine vectors and the same typed metadata predicate across the new database adapters. It resolves eligibility in a session metadata catalog, then pushes eligible IDs into native retrieval. This ensures a Boolean is distinct from the integer one and missing metadata has the same behavior. Native lesson scripts also exercise field predicates directly. [Shared adapter](../common/stores/database.py) · [Coverage map](FEATURE_MAP.md).
