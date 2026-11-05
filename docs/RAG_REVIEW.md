# RAG claim-support review

Reviewed November 5, 2026 by the coding assistant directly against the recorded passages. This is a small assistant-authored qualitative review, **not independent human annotation**. The [final raw run](../results/tier4/rag-ede10bad.json) contains the complete draft, served text and retrieved evidence for each case. The [earlier unguarded run](../results/tier4/rag-75f029f3.json) preserves the initial behavior.

## Rubric

For each factual claim, check whether the cited/retrieved passage entails it. Label it supported, contradicted or unsupported. Separately check that citation IDs exist, the answer addresses the question, includes the required policy details, and stops cleanly. An irrelevant but source-supported claim remains a relevance defect. An incomplete fragment is not counted as a complete factual claim. Abstention avoids unsupported claims but may fail an answerable question.

## Reviewed drafts

| Question | Exact retrieval draft | IVF draft | LSH draft |
|---|---|---|---|
| rag-000, buyer/north return | Return steps, ID reminder and refund timing are supported. No citations; unrelated refund detail. | Return, payment and address claims match their respective passages. Payment/address lists are irrelevant to the return question. | Empty evidence; abstained on an answerable question. |
| rag-001, buyer/north refund | Refund timing and keeping the order ID are supported. The instruction to include payment credentials contradicts the explicit prohibition in the source. A valid source ID does not rescue this answer. | Refund timing, buyer/region applicability and ID reminder are supported. Cancellation detail is extraneous. | Refund timing is supported. Treating contact with support as the way to check a refund is not explicitly established by the source. No citations. |
| rag-002, buyer/north tracking | Tracking via Orders, retaining the ID and avoiding credentials are supported. The timing condition after carrier handoff is omitted. | Tracking steps, handoff condition and credential prohibition are supported. | Empty evidence; abstained. |
| rag-020, buyer/east return | Return procedure and refund/payment statements match their sources. Extra policy sections distract from the question. | Return, payment and address statements match their sources; extra sections are irrelevant. | Empty evidence; abstained. |
| rag-040, seller/north return | Completed return, refund and cancellation claims are supported. The final payment heading is truncated. | Completed return, payment and address claims match their sources. Extra sections are irrelevant. | Empty evidence; abstained. |
| rag-060, seller/east return | Completed return, refund and cancellation claims are supported. Extra sections are irrelevant. | Return, payment and address claims match their sources. Extra sections are irrelevant. | Empty evidence; abstained. |

Among the twelve exact/IVF drafts, at least one contains a direct contradiction, one omits citations entirely and one ends with a truncated fragment. Several violate the requested two-sentence limit. These categories overlap. This review does not estimate population faithfulness, and does not assign a misleading aggregate score to a tiny convenience sample.

## Served output

All twelve exact/IVF cases in this run used the disclosed extractive fallback. Each returned the first two sentences of the top retrieved policy passage and its stable citation ID. Inspection confirms that these twelve excerpts support the requested return, refund or tracking policy and preserve the relevant role/region. One LSH case had sufficient retrieved evidence and also used an excerpt. The other five LSH cases abstained due to missing evidence.

The check is deliberately restrictive: even a good paraphrase falls back unless it exactly matches an approved excerpt. It proves textual correspondence to retrieved material, not that a policy is current, authorized, complete or the correct answer to an arbitrary question. Default UI help displays passages; generation is opt-in. The dataset has 80 answerable questions, so empty-evidence checks do **not** measure broad unanswerable-question detection.

## Retrieval impact

Exact and IVF retrieved the labeled source passage for all 80 questions. The narrow one-table, ten-bit LSH configuration recovered only 3 of 80 source passages. This is an intentionally poor actual index configuration, not simulated candidate loss. It explains five abstentions in the six-question generation sample. The point is to measure evidence loss directly instead of assuming every approximate index damages answers equally.

## Continue the evaluation

Use the same rubric for a larger independent sample including genuinely unanswerable questions, conflicting policies, document instructions, role ambiguity, outdated sources and questions about private order state. Keep draft support, served support, answer correctness, completeness, citation coverage and abstention accuracy separate. A full RAG course should develop those datasets and checks before treating this demonstration as a support system.
