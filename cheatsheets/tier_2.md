# Tier 2 | Approximation and compression

## Choose the search shortcut

LSH groups likely neighbors by hashes. IVF searches selected centroid partitions. HNSW navigates a neighbor graph. Each saves work by risking missed neighbors; exact search remains the reference.

## Tune one control at a time

LSH: tables/bits/probes. IVF: nlist/nprobe. HNSW: M/efConstruction/efSearch. Start with query effort, then rebuild if no quality/cost point qualifies. Do not tune on final evaluation queries.

## Compress with explicit costs

Scalar quantization reduces coordinate precision. PQ learns subvector codebooks. Binary methods store bits. Count codebooks, graph links, IDs and retained full vectors; a one-bit code is not the entire service footprint.

## Filters and hybrid retrieval

Compute truth inside the eligible set. Postfiltering a small global candidate list can miss nearly every eligible neighbor. Fuse dense and lexical ranks with RRF when raw scores are incompatible: contribution = 1/(constant + rank).

## Recorded caution

The first scratch HNSW fixture scored 0.896 against a 0.900 target. A higher-budget validation reached 1.000 with greater memory and latency. Read the workload details in docs/PHASE_4_REPORT.md before generalizing.

## Run and explain

uv run --extra libs python scripts/run_bench.py configs/bench/faiss_exact.yaml
Use the existing configs/bench files for your installed backend. Report recall, p95, errors, build time, resident memory and persisted bytes. See docs/INDEX_TUNING_GUIDE.md.
