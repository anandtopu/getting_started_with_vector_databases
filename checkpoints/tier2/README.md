# Tier 2 checkpoint · choose an index for Marlowe

Deliver TinyVec with IVF, a layered graph, product quantization, metadata filters, lexical ranking and hybrid retrieval. Write a decision for a team choosing an index for a local catalog. Allow 45–60 minutes after Modules 05–10. The [reference submission](results/README.md) links actual raw runs.

## Build and measure

1. Complete the 18 exercises and run their acceptance checks. Run `uv run pytest tests/test_tier2_indexes.py` for snapshot, reachability, compression and filtering checks.
2. Choose a recall floor and latency budget **before** reading the test results. The course fixture floors are LSH 0.60, IVF 0.85, HNSW 0.90 and PQ with rescoring 0.80 at k=10. Record a separate catalog requirement and the hardware available.
3. Install `libs` for FAISS and USearch. Add `hnswlib` for the additional native comparison. On Windows the pinned hnswlib source release needs a C++ compiler. The command below writes new raw runs to an isolated output directory.
4. Read its decision JSON. Each family lists the candidate development runs, chosen settings, held-out raw report and fixture results where applicable. Inspect query counts, splits, warm-up, repeat variation, payload bytes, peak RSS and snapshot bytes. Report misses as misses.
5. Run the boots use case and the million-vector experiment. Explain an eligible product that postfiltering missed, or demonstrate the mechanism on the module's strict-filter experiment. Report measured disk cost separately from an estimate at another size.
6. Open the Playground Index lab. Change the degree and query beam. Describe which changes rebuild the graph, which affect query work, and why one saved query cannot settle the decision.

```sh
uv run --extra libs --extra hnswlib python scripts/checkpoint_tier2.py --output .cache/marlowe/tier2/checkpoint
uv run python modules/10_filtering_hybrid/use_case/boots_under_budget.py
uv run python scripts/measure_disk_scale.py --rows 1000000
uv run --extra apps streamlit run playground/app.py
```

For a shorter run add `--family ivf`. To run without a C++ compiler, use just `--extra libs`; the checkpoint prints a skip for hnswlib and still runs FAISS and USearch.

## Written submission

| Provide | What a reviewer can check |
|---|---|
| Workload and target | Model, row count, metric, k, query split and eligibility rules match across compared rows. |
| Baseline and tuning | Exact neighbors supply truth. The test split stays out of parameter selection. |
| Correctness and relevance | Report neighbor recall separately from judged precision, MRR and nDCG. |
| Performance | Give p50/p95, repeated QPS, build time, peak process RSS, index payload and snapshot size. |
| Trade-off | Explain one setting that helped, one that missed a target and whether measured cost warrants changing engines. |
| Reproduction | Link exact commands, configuration, raw runs and hardware. State how rebuild-on-load and OS page caching affect interpretation. |

## Ready to move on when you can…

- Predict how additional hash tables, probes, graph links and search beam width change candidate generation.
- Explain why a compressed code, full rescoring vector, graph adjacency and process RSS have different byte counts.
- Trace a filtered query across an ineligible bridge and fuse a keyword and semantic ranking.
- Distinguish a mapped scan, a disk graph and a remote object read.
- Choose an engine for a stated recall and latency budget and defend that choice with a measured result.
