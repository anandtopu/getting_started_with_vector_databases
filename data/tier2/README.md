# Offline model sample

These files let Module 08 compare trained embedding prefixes and Module 10 replay a real second-stage ranking on a CPU without loading either model. The first 128 products come from the synthetic Marlowe catalog. The NPZ contains product IDs, full 1024-dimensional float32 document vectors and one query vector. Normalize each prefix after slicing. The reranker JSON lists twelve dense candidates in original rank order with one jointly computed relevance score per query–document pair.

[Manifest with query, revision and SHA-256 hashes](manifest.json) · [Reranking scores](reranking.json) · [Regeneration script](../../scripts/build_tier2_model_sample.py).

To regenerate from cached weights use `uv run --extra models python scripts/build_tier2_model_sample.py`. Add `--download` to fetch the pinned files on first use. The optional Qwen weights alone are about 1.2 GB. Only derived vectors, IDs and scores are included here. Upstream model information: [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B) and [MS MARCO MiniLM cross-encoder](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2).
