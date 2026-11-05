# Measured application results: 17_product_search

[search raw JSON](../../../results/tier4/search-f18a966d.json) · [multilingual raw JSON](../../../results/tier4/multilingual-31cad7d1.json)

| Version | Held-out type | Queries | nDCG@10 | MRR | Precision@10 |
|---|---|---|---|---|---|
| v1_dense | filtered | 10 | 1.0000 | 1.0000 | 1.0000 |
| v1_dense | keyword | 10 | 0.0000 | 0.0000 | 0.0000 |
| v1_dense | misspelled | 10 | 1.0000 | 1.0000 | 1.0000 |
| v1_dense | multilingual | 10 | 0.0000 | 0.0000 | 0.0000 |
| v1_dense | semantic | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_hybrid | filtered | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_hybrid | keyword | 10 | 1.0000 | 1.0000 | 0.1000 |
| v2_hybrid | misspelled | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_hybrid | multilingual | 10 | 0.0000 | 0.0000 | 0.0000 |
| v2_hybrid | semantic | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_reranked | filtered | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_reranked | keyword | 10 | 1.0000 | 1.0000 | 0.1000 |
| v2_reranked | misspelled | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_reranked | multilingual | 10 | 0.0000 | 0.0000 | 0.0000 |
| v2_reranked | semantic | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_typo | filtered | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_typo | keyword | 10 | 1.0000 | 1.0000 | 0.1000 |
| v2_typo | misspelled | 10 | 1.0000 | 1.0000 | 1.0000 |
| v2_typo | multilingual | 10 | 0.0000 | 0.0000 | 0.0000 |
| v2_typo | semantic | 10 | 1.0000 | 1.0000 | 1.0000 |

| Model on matched 500 products | Held-out multilingual nDCG@10 |
|---|---|
| MiniLM | 0.0000 |
| Qwen | 1.0000 |

Parser exact-match coverage: 250/250. Retrieval timing: `{"p50_ms": 19.063250001636334, "p95_ms": 155.2260900120018, "p99_ms": 165.46786201157374, "samples": 250, "queries": 50, "repetitions": 5, "warmup": 20, "qps": 22.078924311972045, "embedding_excluded": true, "reranking_excluded": true}`. Only 50 held-out text queries exist in the supplied judgment set, below the preferred 100-query benchmark size. Five repetitions produce 250 timings, not 250 independent questions. Reranking is a separately timed single-pass quality diagnostic. Initial unprotected SKU reranking is preserved in the earlier raw run.


Backend: **qdrant-local**, a single owned local Qdrant client per application evaluation. Hardware and package versions are embedded in every raw JSON. Model identities and content hashes are in the linked run's artifact manifests. Judgments are synthetic. No hosted service was used.

[Comparison plot](../../../checkpoints/tier4/results/comparison.png) · [Method and reproduction](../../../checkpoints/tier4/README.md)
