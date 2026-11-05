# Phase 3: Tier 1 is ready to study

Tier 1 takes a learner from a product search that exact wording misses to an exact vector store they can build, restore, and measure. Start at [Module 00](../modules/00_setup/README.md); finish with the [Tier 1 checkpoint](../checkpoints/tier1/README.md). The default path uses included catalog vectors and requires no account, model download, or Docker service after installing dependencies.

| Lesson | What the learner can verify | Measured evidence |
|---|---|---|
| [00 · Setup](../modules/00_setup/README.md) | A literal phrase returns no products; the saved semantic query finds five useful mug warmers. | [Search results](../modules/00_setup/results/README.md) |
| [01 · Vectors and similarity](../modules/01_vectors_similarity/README.md) | Predict ranking changes under cosine, dot product, and L2; see distance spread shrink as dimensions increase. | [Geometry and timings](../modules/01_vectors_similarity/results/README.md) |
| [02 · Embeddings](../modules/02_embeddings/README.md) | Plot the catalog using PCA, identify what the map loses, and measure real model inference separately from cache hits. | [Projection and cache measurements](../modules/02_embeddings/results/README.md) |
| [03 · TinyVec](../modules/03_tinyvec/README.md) | Insert, update, delete, filter, and restore records; observe how applying a filter too late loses an eligible product. | [Filter experiment](../modules/03_tinyvec/results/README.md) |
| [04 · Benchmarking](../modules/04_benchmarking/README.md) | Separate exact-neighbor recall from judged relevance, and compare latency and throughput on matching inputs. | [Quality and timing results](../modules/04_benchmarking/results/README.md) |

Each module includes a notebook, a product use case, three starter exercises with reference solutions, and six quiz questions with answers. The five modules share [a vocabulary guide](../modules/TIER1_TERMS.md). TinyVec now has an independently callable [exact search kernel](../tinyvec/exact.py) and distinguishes strict insert from upsert. The [FAISS adapter](../common/stores/faiss_flat.py) follows the same filter and tie rules as TinyVec. Chroma and LanceDB also run as native teaching examples; the Playground lets learners try TinyVec, SQLite-vec, or FAISS.

## What ran on November 4, 2026

| Check | Local result |
|---|---|
| Installed-environment test suite | 122 passed; 3 outside the default test selection. |
| Base-only test suite | 71 passed; 51 optional checks skipped; the same 3 outside the default selection. |
| Example runner | 24 passed with no skips: 3 foundation examples, 16 Tier 1 examples, and 5 use cases. |
| Exercise checks | All 15 starters passed their smoke checks; all 15 reference solutions passed their acceptance cases. A starter is runnable before it solves the exercise. |
| Notebook execution | All 26 code cells across five notebooks ran offline with the native libraries installed. Source notebooks retain no outputs. |
| Measurements | 11 new configurations ran 20 warm-ups and five repetitions of 100 queries each: 5,500 timed requests. Raw reports and plots are linked from the [leaderboard](../results/leaderboard.md). |
| Checkpoint | A fresh Python process restored the same five IDs. The [reference submission](../checkpoints/tier1/results/README.md) records the independent checkpoint benchmark and the Playground interaction before and after filtering. |

## Interpreting two matched results

Both engines searched the same 1,000 catalog products with cosine similarity, the same 100 queries, k=10, and one numerical-library thread. These measurements were taken on Windows 11, Python 3.12.13, with 24 reported CPU cores and 31.46 GiB of RAM.

| Exact engine / raw run | Neighbor recall@10 | Judged nDCG@10 | p50 / p95 (ms) | Serial QPS, mean ± SD |
|---|---:|---:|---:|---:|
| [TinyVec](../results/runs/benchmark-method-20261104T223931-d8ebddb7.json) | 1.0000 | 0.8402 | 0.481 / 1.043 | 1,569.4 ± 67.5 |
| [FAISS flat adapter](../results/runs/faiss-exact-20261104T223936-4644c6de.json) | 1.0000 | 0.8402 | 0.360 / 1.059 | 1,928.2 ± 51.1 |

FAISS had a lower median retrieval time here, but its p95 was slightly higher. The comparison includes adapter work such as filtering and stable tie ordering; it does not measure bare FAISS or concurrent service performance. Both stores reproduced the exact neighbors, yet precision@10 was only 0.654 against the synthetic judgments. A faster exact search alone would not improve the usefulness of those results.

In [the embedding experiment](../modules/02_embeddings/results/README.md), cached MiniLM weights took 6.44 s to load. The first cache pass took 401.80 ms and the median subsequent hit took 18.79 ms. Those times are separate from retrieval latency. In the checkpoint, adding a $30 ceiling and choosing the north region removed a $30.33 western product and returned a $24.89 northern one instead.

## Reproduce the checks

Use the [setup guide](SETUP.md) for environment commands and the [checkpoint rubric](../checkpoints/tier1/README.md) for the submission steps. Each module links the command and configuration behind its numbers. The [measurement guide](../results/README.md) defines timing boundaries, tie handling, and comparison groups.

Local execution covered Windows and in-process libraries. Hosted CI, macOS, physical low-memory hardware, and Docker server deployments were not tested in this phase. Approximate indexes and the Tier 2 curriculum are outside Phase 3.
