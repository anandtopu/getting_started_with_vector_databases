# Measured application results: 18_rag

[rag raw JSON](../../../results/tier4/rag-ede10bad.json)

| Retrieval | Source passage recall@4 |
|---|---|
| Exact | 1.0000 |
| IVF, 8 lists, 1 probe | 1.0000 |
| LSH, 10 bits, 1 table | 0.0375 |

The small corpus makes IVF easy; the narrow LSH configuration exposes candidate loss. See the raw record for per-question sources, draft answers, served excerpts, citations and generation time. [Claim-support review](../../../docs/RAG_REVIEW.md) separates citation syntax, factual support, relevance and completeness. Draft quality is insufficient for direct delivery. The application uses a transparent extractive fallback.


Backend: **qdrant-local**, a single owned local Qdrant client per application evaluation. Hardware and package versions are embedded in every raw JSON. Model identities and content hashes are in the linked run's artifact manifests. Judgments are synthetic. No hosted service was used.

[Comparison plot](../../../checkpoints/tier4/results/comparison.png) · [Method and reproduction](../../../checkpoints/tier4/README.md)
