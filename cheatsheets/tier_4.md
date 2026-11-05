# Tier 4 | Search applications

## Product retrieval

Parse structured price/stock/region constraints, retrieve lexical and dense candidates, fuse ranks, then optionally rerank. Keep seller scope mandatory. Evaluate semantic, exact-SKU, typo and multilingual queries separately.

## Help-center RAG

Chunk with stable passage IDs; retrieve evidence; apply an abstention rule; return citations. Source excerpts are extractive responses, not LLM generations. A valid citation can still point to the wrong policy.

## Recommendations and duplicates

Exclude the item itself and previously seen items where appropriate. Evaluate recommendations using time-aware event splits. Choose duplicate thresholds using positives and hard negatives; report false merges as well as missed duplicates.

## Photo search

Use compatible image/text encoders and track modality in cache keys. Named vectors or separate collections preserve representation identity. Weighted rank fusion combines branches without comparing incompatible raw scores.

## Run the demo

uv run --extra apps --extra qdrant streamlit run playground/marlowe.py
Saved queries use included embeddings. Custom queries and generation need explicit model setup; see docs/TIER4_APPLICATIONS.md.

## Evaluate four different questions

Did ANN recover the exact neighbors? Are those neighbors relevant? Does the cited passage exist? Does every answer claim follow from that evidence? Record these independently, including abstention and answerability. See Modules 17-20 and capstone 03.
