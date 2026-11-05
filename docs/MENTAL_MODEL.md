# A mental model of vector search

An embedding is a list of numbers that a model assigns to an input. Similarity is a rule for comparing two lists. An index is a shortcut for finding good candidates. A database adds durable records, updates, filters, and operational behavior. These are separate choices.

```mermaid
flowchart TD
    D[Products, documents, or images] --> P[Prepare text, chunks, or pixels]
    P --> E[Versioned embedding model]
    E --> V[Vectors plus IDs and metadata]
    V --> S[Persistent record storage]
    V --> I[Exact scan or approximate index]
    Q[User query] --> QE[Same compatible embedding space]
    QE --> F[Eligible records from filters]
    F --> I
    I --> C[Candidate IDs and scores]
    K[Keyword search] --> H[Optional hybrid merge]
    C --> H
    H --> R[Optional reranker]
    R --> A[Search, recommendations, or retrieved context]
    S --> A
    A --> G[Optional answer generation with citations]
    A --> M[Measure relevance, latency, resources]
    M --> T[Tune on development queries]
    T --> I
```

The foundation implements preparation, cached text embeddings, exact scans, storage, filters, and measurement. Hybrid retrieval, reranking, approximate indexes, and full answer evaluation are later lessons.

Three questions keep the layers straight: **Did the index find the model's nearest neighbors?** Measure neighbor recall. **Were those neighbors useful answers?** Measure relevance with independent judgments. **Was the result fast and affordable enough?** Measure latency, throughput, memory, and disk on the intended workload.

A filter changes which records are eligible. Exact filtered ground truth must search that same eligible set. A two-dimensional plot loses information and cannot replace distance calculation in the full vector space. A different model revision or preprocessing recipe creates a different space even if the vector length stays the same.
