# Build a durable indexed TinyVec

Prerequisites: Tier 2 and B2. Budget: one afternoon for the baseline, longer for the measurements and extensions. Use Python 3.12 and the repository's locked environment. Work from the repository root.

## User stories

- As a search developer, I can choose HNSW or PQ while preserving one CRUD/filter contract.
- As an operator, I can save, reopen, and confirm deleted IDs never return.

## Build and run

1. Run the starter smoke command below. The starter is a small working baseline, not a finished submission.
2. Read [architecture](architecture.md), then fill the `YOUR CODE HERE` work in `starter/project.py`. Keep the exported contract named in the acceptance tests.
3. Run acceptance against your file. Inspect the reference only after attempting the contract.
4. Run the measured reference and write your own decision with raw evidence.

```sh
uv sync --locked --extra libs --extra embedded --extra apps --extra qdrant --extra ops
uv run python scripts/check_capstone.py capstones/01_tinyvec/starter/project.py --smoke
uv run python scripts/check_capstone.py capstones/01_tinyvec/starter/project.py
uv run python scripts/check_capstone.py capstones/01_tinyvec/solution/project.py
uv run python capstones/01_tinyvec/solution/project.py --evaluate
```


## Acceptance criteria

- Implement build(kind, records, spec) and restore(path) in starter/project.py.
- Preserve metadata filters and model-space identity after restore.
- Measure both indexes and FAISS exact search on the same 500 vectors; report recall, p95, memory and build cost.

The executable contract is [tests](tests/test_01_project.py); [evaluation configuration](evaluation.yaml) identifies entry points. These compact checks are necessary behavioral tests, not complete security or statistical certification. [Rubric](rubric.md) requires the broader measurements and explanation.

## Evidence and limits

See [measured reference results](results/README.md). IndexedTinyVec retains full vectors for rescoring. PQ code bytes are not total resident memory. The 100-row acceptance fixture tests behavior; the 500-row measured comparison is descriptive, not proof of large-scale ANN quality.

## Clean up

Reference sessions remove owned temporary collections. Stop course services with the command in the Tier 5 runbook. Run `python scripts/cleanup.py` to inspect generated cache/data before confirming deletion; keep included fixtures and shared model caches. See [extensions](extensions.md).
