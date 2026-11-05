# Module 10 · Filtered, hybrid and multi-vector retrieval

> Return useful boots that satisfy the customer's price, stock and region constraints.

**Time** 120 minutes · **Level** Intermediate · **Needs** Python 3.12, local CPU and the included catalog. Allow about 8 GB system RAM for the teaching environment. Install the library extra for the native comparison. Docker and online inference are unnecessary. 

**TinyVec and Marlowe Search version 5.** Return useful boots that satisfy the customer's price, stock and region constraints. [Measurements and raw evidence](results/README.md).

## Prerequisites

Complete [Module 09](../09_disk_scale/README.md). Run commands from the repository root. The [Tier 2 vocabulary](../TIER2_TERMS.md) defines terms used across these lessons. Install once with `uv sync --locked --extra libs`. Use `--extra embedded` for sqlite-vec and LanceDB, or `--extra hnswlib` for the optional compiled graph library. The [setup guide](../../docs/SETUP.md) includes the base environment instructions.

## Learning objectives

- Return useful boots that satisfy the customer's price, stock and region constraints.
- Trace the candidate IDs through the diagram and identify where an eligible neighbor can be lost.
- Reproduce the measured experiment and distinguish the observed resource cost from an estimate.
- Explain the product decision in the use case using a specific result.

## The big idea

A shopper asks for waterproof hiking boots under $100, in stock, in the north region. A semantically ideal boot outside the budget is ineligible. A product code typed verbatim is a different kind of clue. To serve both requests, separate eligibility from the evidence used to rank eligible products.

## How it works

```mermaid
flowchart LR
    n0["Price stock region"] --> n1["Eligible rows"] --> n2["Dense and sparse rankings"] --> n3["Reciprocal rank fusion"] --> n4["Rerank candidates"]
```

An equality posting maps a metadata value to row IDs. Intersect postings before checking ranges. A naive postfilter keeps eligible hits from an unfiltered shortlist and can return too few. An adaptive plan scores small eligible sets exactly. A graph-aware plan can traverse through an ineligible bridge and accept only eligible results. Measure neighbor recall against an exact search inside the eligible set.

BM25 stores sparse term-to-document postings, term frequency and document length. A rare SKU can outrank common words. Reciprocal rank fusion (RRF) adds 1/(constant+rank) across lists so scores from dense and lexical search need no common scale. For multiple vectors per document, MaxSim sums each query token's highest document-token similarity. A cross-encoder instead reads the query and candidate text together and assigns a second-stage score.

## Build it yourself

Trace the postings and length normalization in tinyvec/hybrid.py. A term occurring in many documents carries less evidence. Compare two product titles with a rare SKU. For late interaction, use a query with one token about warmth and one about a desk. Different document tokens can supply their best matches. [TinyVec implementation](../../tinyvec/hybrid.py) · [Scratch example](examples/01_from_scratch.py).

```sh
uv run python modules/10_filtering_hybrid/examples/01_from_scratch.py
```

## Now in a real database

Use bm25s to retrieve actual product titles, then run the LanceDB hybrid example. LanceDB stores multiple token vectors per row alongside a dense vector. The native full-text and dense candidate lists are fused first. A readable token-feature scorer reranks that shortlist. A separate cached example uses scores from the pinned MiniLM cross-encoder over twelve actual MiniLM candidates. [Native example](examples/02_production.py). [lance hybrid](examples/04_lance_hybrid.py)

```sh
uv run --extra libs python modules/10_filtering_hybrid/examples/02_production.py
```

## Walkthrough

The indexed store includes the SKU field in its lexical postings. If the entire query matches an eligible SKU exactly, it adds an explicit identifier bonus to that item's fused score. An ineligible SKU receives no bonus because both ranking branches filter candidates first.

Run the boots query. Check price, region and stock on every returned row before comparing order. In the filtering experiment, inspect the raw per-type metrics for keyword and filtered requests separately. The dense exact neighbor is a reference for vector similarity. For hybrid rankings, precision, MRR and nDCG answer whether the changed order fits the synthetic judgments. Open [the notebook](notebook.ipynb), predict the outcome of its last code cell, then change one input and explain what changed. The notebook mirrors the scripts so you can compare each result with a terminal run.

## Measure it

```sh
uv run python modules/10_filtering_hybrid/examples/03_measure.py
uv run --extra libs python scripts/run_bench.py configs/bench/tier2/hybrid-rrf.yaml
```

The first command isolates one lesson observation. The shared catalog benchmark warms up, repeats shuffled queries five times and scores against independently computed eligible neighbors. Compare query sets, k, hardware and embedding space before comparing QPS. [Module results](results/README.md) · [Benchmark methodology](../../results/README.md).

## When to use it, and when not to

Use hybrid search when literal terms and semantic intent both matter. A costly second stage makes sense only after retrieval has enough relevant candidates. Benchmark with real query lengths and account for reranking time separately.

## Real-world use case

A buyer enters a phrase plus constraints. Use indexed metadata to enforce eligibility, then let lexical SKU matches and semantic product meaning vote on the remaining items. Keep both the query text and embedding space in the audit trail. [Run the use case](use_case/boots_under_budget.py).

```sh
uv run python modules/10_filtering_hybrid/use_case/boots_under_budget.py
```

## Common mistakes

- Filtering after a small shortlist can discard all eligible products.
- Dropping ineligible traversal nodes can disconnect the search.
- Raw BM25 and cosine scores do not share units.
- A second-stage model cannot retrieve an absent candidate.

## Exercises

### Practice · Intersect metadata postings

Return the sorted intersection of IDs present in both postings. For inputs `[[1,2],[2,3]]`, expect `[2]` (JSON notation). Start with the [starter](exercises/01_practice.py) and check your answer with this command. Compare with the [reference solution](solutions/01_practice.py) after trying it.

```sh
uv run python scripts/check_exercise.py modules/10_filtering_hybrid/exercises/01_practice.py
```

### Apply · Fuse ranked IDs

Use one vote per ID per ranking with a reciprocal-rank constant of 60. Return at most k IDs. For inputs `[[["a","b"],["b"]],2]`, expect `["b","a"]` (JSON notation). Start with the [starter](exercises/02_apply.py) and check your answer with this command. Compare with the [reference solution](solutions/02_apply.py) after trying it.

```sh
uv run python scripts/check_exercise.py modules/10_filtering_hybrid/exercises/02_apply.py
```

### Stretch · Score a token interaction

Sum the largest value in each query-token row, including when all values are negative. For inputs `[[[1,4],[3,0]]]`, expect `7` (JSON notation). Start with the [starter](exercises/03_stretch.py) and check your answer with this command. Compare with the [reference solution](solutions/03_stretch.py) after trying it.

```sh
uv run python scripts/check_exercise.py modules/10_filtering_hybrid/exercises/03_stretch.py
```

## Quiz

1. What makes a sparse vector sparse?

<details><summary>Answer</summary>

Only the few present terms have stored nonzero weights.

</details>

2. Why can postfiltering lose recall?

<details><summary>Answer</summary>

Eligible rows may never enter the shortlist.

</details>

3. Why traverse ineligible graph nodes?

<details><summary>Answer</summary>

They may be the only bridge to eligible rows.

</details>

4. How does RRF combine scores?

<details><summary>Answer</summary>

It sums contributions based on rank positions.

</details>

5. How does MaxSim differ from one vector per product?

<details><summary>Answer</summary>

Each query token can match a different document token.

</details>

6. Why measure relevance separately from neighbor recall?

<details><summary>Answer</summary>

Fusion can improve useful results while changing their vector-neighbor order.

</details>

## Key takeaways

- Return useful boots that satisfy the customer's price, stock and region constraints.
- Only the few present terms have stored nonzero weights.
- They may be the only bridge to eligible rows.
- It sums contributions based on rank positions.
- Fusion can improve useful results while changing their vector-neighbor order.

## Clean up

Examples use temporary directories for native stores and mappings. Stop Jupyter or the Playground with Ctrl+C. Diagnostic reports live under `.cache/marlowe/tier2`. To inspect course-owned cleanup paths, run `uv run python scripts/cleanup.py`. The measured evidence linked from this lesson is retained in the repository.

## Go deeper

Read the [primary reference](https://arxiv.org/abs/2004.12832) alongside the [recorded results](results/README.md). 

## Next: Module 11 after the checkpoint

Complete the [Tier 2 checkpoint](../../checkpoints/tier2/README.md) then continue to [Module 11](../11_embedded/README.md).
