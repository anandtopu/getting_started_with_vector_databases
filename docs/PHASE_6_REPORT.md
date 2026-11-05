# Phase 6 delivery: Tier 4 applications

Delivered locally November 5, 2026, version 0.6.0. Modules 17–20 and the Tier 4 checkpoint implement Marlowe Search v2–v5. The repository is not a Git checkout, so no commit, remote publication or hosted CI run was performed.

## Delivered scope

- [Module 17](../modules/17_product_search/README.md): conservative query constraints, eligible hybrid ranking, typo handling, real cross-encoder reranking with an exact-SKU policy, and a matched multilingual model comparison.
- [Module 18](../modules/18_rag/README.md): passage-preserving chunking, metadata-scoped retrieval, actual local Ollama generation, citations, source-excerpt fallback, and exact/IVF/LSH evidence-recall comparison.
- [Module 19](../modules/19_recommendations/README.md): item and event-derived recommendations, MMR, temporal evaluation, held-out duplicate calibration, review themes and outlier inspection.
- [Module 20](../modules/20_multimodal/README.md): real SigLIP image/text vectors, text-to-image and photo retrieval, native Qdrant named vectors, weighted rank fusion and self-match-free evaluation.
- [Tier 4 checkpoint](../checkpoints/tier4/README.md): a shared service, FastAPI endpoints and Streamlit UI combining all five application capabilities on a selected database backend.

The four modules include **18 examples, four use-case scripts, twelve runnable exercise starters and reference solutions, four cleared mirrored notebooks, 24 quiz questions, complete lesson READMEs and measured result pages**. Ten feature configurations link to actual execution evidence and leaderboard anchors.

## What the evidence shows

[Comparison tables and plot](../checkpoints/tier4/results/README.md) are generated from immutable raw observations.

| Application | Observed result | Interpretation |
|---|---|---|
| Search | All 250 text queries receive typed-query evaluation; held-out rows cover five query types. Exact SKU protection repairs the generic reranker's initial identifier failure. | An explicit business rule is useful even with a learned model. |
| Multilingual | On the same 500 products, held-out Spanish nDCG@10 is 0.000 for MiniLM and 1.000 for Qwen. | This is ten held-out synthetic families, not broad multilingual validation. |
| RAG retrieval | Source passage recall@4: exact 1.000, IVF 1.000, narrow one-table LSH 0.0375 over 80 questions. | Approximate settings can remove answer evidence; IVF lost none on this small corpus. |
| RAG delivery | A real draft contradicted the source's credential policy. All twelve reviewed exact/IVF answers used a disclosed cited-excerpt fallback. | Valid citation IDs do not prove faithfulness. [Qualitative review](RAG_REVIEW.md). |
| Recommendations | Future-item recall@10 is 0.010, 0.020 and 0.010 for MMR weights 1.0, 0.7 and 0.3 over 100 synthetic users. Diversity rises as similarity weight decreases. | Synthetic preferences and sparse future purchases produce modest recall. No conversion-lift claim. |
| Duplicates | Development-selected cosine threshold 0.934855 gives precision/recall 1.000 on 80 held-out pairs. | Easy planted duplicates and only the 400 pairs covered by the committed catalog. |
| Photo search | Held-out nDCG@10 is 0.4937 text-to-image, 0.5500 photo and 0.7104 fused. | 200 synthetic drawings, ten held-out families, exact self-image excluded; not real-photograph validation. |

Search timing uses 20 warmups and five passes over 50 held-out text queries, for 250 latency samples. The corpus supplies only 50 such queries, below the preferred 100 independent-query benchmark size. Reranking is a separate single-pass quality diagnostic. Retrieval, model inference and whole-script startup are not mixed into a database leaderboard. Hardware, installed versions, model/content hashes and individual outputs are retained in the raw JSON.

## Implementation decisions and observed fixes

The complete reference uses Qdrant local mode for a low-resource one-backend application, with native named photo vectors. This does not claim server HNSW or distributed behavior. The complete API lifecycle is also checked on TinyVec and SQLite. SQLite exposed a model-switch path collision during integration testing; application collection paths are now unique even when their logical role names match.

The original event generator repeats seen products and assigns one action type per user. Its first 100-user audit had zero evaluable unseen-purchase cases. That failed measurement remains in [the initial result](../results/tier4/recommendations-74591b16.json). A separate **700-event, 100-user fixture** now supplies five past interactions and two distinct future purchases per user, with product-kind preferences chosen independently of embedding scores. The original data is unchanged.

The raw reranking failure is retained in [the initial search result](../results/tier4/search-e70bb813.json). The general identifier rule is applied after reranking and never introduces ineligible records. Parser negation handling was narrowed to constraint phrases so “a clock that does not tick” does not disable valid price and stock clauses. Affected saved query vectors were regenerated, and content checks now reject stale query artifacts.

Ollama's initial unconstrained-thread run failed to complete reliably on this host. Four CPU threads and bounded output completed the recorded calls. The model's unsupported draft remains visible in raw evaluation. The UI defaults to retrieved passages, and opt-in generation uses a conservative source-excerpt delivery policy. The model is still unsuitable for unrestricted support answers.

The repository includes the small review, event, duplicate and gallery source fixtures needed for offline lessons, plus genuine MiniLM/Qwen/SigLIP vectors. Custom text, a resized image and text-to-image inference were exercised through the integrated service. [Custom inference record](../research/phase6-custom-inference.json).

## Verification

- Full installed-environment regression suite: **231 passed, 11 deselected**.
- Independent base-only environment: **168 passed, 63 skipped, 11 deselected**, optional packages explicitly skipped; Docker/live tests remain deselected.
- All **22 new examples and use cases passed**, with zero skips in the explicit verification run. [Execution record](../results/tier4/execution-cb02c5e5.json).
- All four new notebooks executed, **26 code cells**, including local generation. The earlier 17 notebooks were verified in Phase 5. All 21 source notebooks remain cleared.
- All twelve reference solutions pass the learner-facing acceptance checks; starter smoke checks pass.
- Actual API lifecycle checks cover TinyVec, Qdrant local and SQLite, including saved multilingual search. Streamlit tests cover all five UI workflows and cleanup.
- Genuine cached model inference was checked for MiniLM custom text, Qwen embedding preparation, cross-encoder reranking, SigLIP image/text preparation and custom input, and Ollama generation.
- Ruff, module structure, local links/anchors, artifact checksums and the offline lock check are part of the final verification. **337 included artifacts** are inventoried.

[Validation inventory](../research/phase6-validation.json) records logs, latest raw runs and scope. Hosted CI was updated but has not run. External links were not exhaustively probed. The actual database server deployments remain Phase 5 evidence; this phase's complete application reference uses the local Qdrant implementation.

## Remaining boundaries

Judgments, policy articles, behavior, duplicate pairs and images are synthetic. The RAG claim review is assistant-authored, not independent human annotation. The 80-question set is answerable and does not establish unanswerable-question detection. Extractive delivery proves correspondence to a retrieved source, not its correctness for an arbitrary question. Review clustering has no human topic/anomaly labels. Memory allowances in setup are planning estimates, not a model peak-RSS study.

Start with [application setup](TIER4_APPLICATIONS.md) or [Module 17](../modules/17_product_search/README.md). Phase 7 is Modules 21–23: data modeling, operations, performance, security and reliability.


## Runtime cleanup

The dedicated Phase 6 Ollama verification container was removed after generation and notebook checks. [Ownership-checked cleanup record](../research/phase6-runtime-cleanup.json). No Phase 6 labeled containers remain. Shared downloaded model and image caches were retained. Start Ollama again to reproduce generation; frozen-vector applications work without it.
