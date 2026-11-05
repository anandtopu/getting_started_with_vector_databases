# Tier 1 checkpoint: an exact search you can explain

Deliver TinyVec v1, a reproducible benchmark report, and a recorded Playground search. No Docker or new model download is needed. Allow 30–45 minutes after completing modules 00–04.

## Build and verify

1. Complete all 15 exercise acceptance checks. Use `scripts/check_exercise.py` with your edited starter paths; reference solutions are available for comparison. Default pytest separately verifies reference behavior and that starters run.
2. Run `uv run python scripts/checkpoint_tier1.py`. It loads real saved vectors, checks useful mug-warmer hits, saves TinyVec, restores it in a **fresh process**, compares IDs, and runs the repeated 1k baseline. Read `.cache/marlowe/tier1/checkpoint/submission.json` and its referenced raw benchmark.
3. Run `uv run --extra apps streamlit run playground/app.py`. Search q000, then add a maximum-price and region filter. Record the selected catalog size, query ID, filter, returned IDs, retrieval time, and one explanation of a changed result. The automated checkpoint does not pretend to complete this learner observation.
4. Write a short report using the structure below. Include the raw run filename and explain one limitation rather than reporting a universal winner.

## Report structure

For an automated reference session, run `uv run --extra apps python scripts/checkpoint_tier1.py --playground`. This records the actual before/after tables using Streamlit's interaction runner; it does not claim browser visual inspection or complete your interpretation. See [the reference submission](results/submission.json) and [reference report](results/README.md).

- Workload: product count, query count/types/split, model space, metric, k, filter, precision.
- Correctness: restore result and neighbor recall, with tie handling explained.
- Usefulness: precision/MRR/nDCG against synthetic judgments; which case still needs human review?
- Cost: retrieval percentiles, serial QPS with repeat variation, insertion/build, process RSS, snapshot bytes.
- Playground observation: before/after IDs for one filter, with an explanation.
- Decision: what can this exact local design support, and which requirement would justify moving to a different architecture?

## Acceptance rubric

| Evidence | Pass condition |
|---|---|
| Exercise behavior | All 15 selected learner implementations pass their acceptance cases |
| Lifecycle | Stable IDs survive a fresh-process snapshot restore; mutations do not return deleted records |
| Correctness baseline | Exact neighbor recall is 1 on the standard configuration under documented tie semantics |
| Relevance | At least one judged result is explained independently of vector distance |
| Timing | Warm-up, repetitions, timing boundaries, hardware, and sample count are stated |
| Playground | A saved query and a filtered query are recorded and explained |
| Limitations | Synthetic judgments, single-owner TinyVec, and local hardware limits are acknowledged |

## Ready for Tier 2 when you can…

- Explain a coordinate without assuming a learned dimension has a human-readable name.
- Predict a normalization-induced ranking change and handle zero vectors.
- Upsert, delete, filter, and reload while preserving stable IDs.
- Distinguish nearest-neighbor accuracy from useful answers.
- Reproduce a benchmark and explain why an apparently faster result might be misleading.
- Explain why test hashing cannot establish semantic quality.

The [Phase 3 report](../../docs/PHASE_3_REPORT.md) contains reference execution evidence. Your own report should describe your machine and observations. Phase 4 introduces approximate indexes only after this exact baseline is understood.

## Cleanup

Close the Playground with Ctrl+C. No containers were started. Preview `uv run python scripts/cleanup.py`; add `--remove` only after reviewing all generated course resources it lists. Keep your report and any raw evidence you intend to submit outside the disposable cache.
