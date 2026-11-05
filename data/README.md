# Marlowe Market data card

Marlowe is fictional. Product names, sellers, reviews, interactions, policy articles, and images are generated locally from templates and seeded random choices. They contain no scraped listings, real customer histories, or private personal data. Code and generated data use the repository's [MIT license](../LICENSE).

## Included and generated artifacts

| Artifact | Size / purpose | Distribution |
|---|---|---|
| `products_10k.parquet` | First 10,000 products with IDs, text, attributes, seller, stock, and tenant fields | Included |
| `embeddings_10k.parquet` | 10,000 × 384 real MiniLM embeddings, float16 storage | Included, about 7.3 MiB |
| `query_embeddings.parquet` | 300 saved text query embeddings | Included |
| `sellers.json` | 300 fictional sellers | Included |
| [Tier 2 model sample](tier2/README.md) | 128 full Qwen product embeddings, one Qwen query and twelve scored cross-encoder candidates | Included for offline lessons |
| `help_center/` | 80 articles across topics, regions, and access roles | Included |
| `eval/search_qrels.jsonl` | 300 queries and graded product IDs | Included |
| `eval/rag_qa.jsonl` | 80 source-linked reference questions/answers | Included |
| `eval/judging_worksheet.csv` | Empty human-review worksheet with headers | Included; no human judgments claimed |
| `fixtures/images/` | 20 generated silhouettes | Included |
| `products.parquet`, `reviews.parquet`, `events.parquet` | 50k products, 100k reviews, 200k interactions | Regenerated; excluded from version control |
| `duplicates.parquet`, `images/` | 1k positive/negative pairs; 2k generated silhouettes | Regenerated |
| `embeddings_full.parquet` | All 50k product vectors | Explicit model preparation; regenerated |

Run `uv run python scripts/build_data.py` from the repository root. The default seed is 20261104 and reference date is 2026-01-01. Generation writes bounded parquet batches. `generated-manifest.json` records generated file hashes. Included embedding manifests record model, revision, preprocessing identity, row count, precision, creation time, and checksum; rows also carry hashes of the source text to catch stale alignment. `manifest.json` inventories the included artifacts.

MiniLM model: `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, Apache-2.0. Model weights are not redistributed here. See the [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) and [verification notes](../docs/VERIFICATION_NOTES.md). Stored vectors are float16-rounded; search promotes them to float32. Recomputed float32 model output will not be bit-identical to the stored representation.

## Relevance and splits

Queries cover semantic needs, exact keywords, structured filters, misspellings, Spanish, and photo requests (50 each). Relevance is generated from category/product-kind, filters, and, for photo requests, color. Exact keyword queries label the specified item. Matching ordinary product kinds receive grade 3. These rules do not consult embedding scores, so model performance cannot create its own labels.

Queries split by product-kind family: every fifth family is test; the others are development. Related phrasings stay in the same split. Initial benchmark configs use `split: all` for descriptive baseline coverage and are **not held-out tuning evaluations**. Use development for tuning and test for later final comparisons.

The catalog intentionally contains repeated variants. Every fiftieth listing clones a prior product as a planted seller relisting, with a new ID and a `duplicate_of` relationship. Duplicate detection labels and search relevance serve different purposes. Close or equal vectors may legitimately yield multiple relevant listings.

Photo query embeddings in this release are **text surrogates**, not image evaluation. They are excluded from the text benchmark harness and Playground saved-query menu. Actual SigLIP image retrieval now has its own [Tier 4 evaluation](../modules/20_multimodal/results/README.md). The surrogate caveat still applies to the older query_embeddings.parquet photo rows. Generated silhouettes are simple controlled shapes without text and are not realistic product photography.

Policy questions have source passages and answerability fields; this small set does not yet evaluate the full later RAG abstention task. Reviews/events are scripted patterns, not evidence of real user preferences. No leaderboard result should be interpreted as human-reviewed marketplace quality. Use the worksheet to add independently reviewed judgments and keep reviewer IDs and split decisions separate from model outputs.

## Optional public benchmark

Fashion-MNIST uses the original [Zalando repository](https://github.com/zalandoresearch/fashion-mnist), pinned source revision and MIT license. [The source manifest](../docs/benchmark_datasets.json) contains exact URLs, lengths, and SHA-256 hashes. The downloader checks bytes before use and retains the source license beside them. It samples 10k training images as base vectors and 1k test images as queries using different fixed seeds, flattens 28×28 grayscale pixels, and scales to [0,1]. No labels or neural embeddings are needed for its L2 neighbor workload. This subset is not a reproduction of full-size published benchmark results.


## Included Tier 4 application artifacts

`data/tier4/` includes real MiniLM help/review/query vectors, Qwen vectors for 500 products and 50 Spanish queries, and SigLIP vectors for a 200-image gallery with paired text and 50 text queries. Every vector file has a model/revision/preprocessing/content manifest. Apache-2.0 pretrained models are identified in `common/embeddings.py`; model weights are not included. All source text, events and drawings are MIT synthetic course data.

Small review (400 rows), original event (40,000 rows), duplicate (400 pairs) and image (200 drawings) subsets make examples independent of the ignored full generated data. Regenerate sources with `scripts/build_data.py`, then `scripts/build_tier4_fixture.py --sources`. The separate 700-event temporal evaluation fixture is generated by `scripts/build_tier4_fixture.py`. It records its independent kind-preference rule and the original event coverage problem in its manifest. Regenerate vectors with `scripts/prepare_tier4.py --all --download`, then explicitly refresh the inventory with `scripts/verify_artifacts.py --refresh`.
