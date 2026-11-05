# Choose a database with evidence

Prerequisites: Tier 3. Budget: one afternoon for the baseline, longer for the measurements and extensions. Use Python 3.12 and the repository's locked environment. Work from the repository root.

## User stories

- As an engineer, I can compare three installed databases using the same vectors and query IDs.
- As a reviewer, I can reject a fast result that fails recall or has errors.

## Build and run

1. Run the starter smoke command below. The starter is a small working baseline, not a finished submission.
2. Read [architecture](architecture.md), then fill the `YOUR CODE HERE` work in `starter/project.py`. Keep the exported contract named in the acceptance tests.
3. Run acceptance against your file. Inspect the reference only after attempting the contract.
4. Run the measured reference and write your own decision with raw evidence.

```sh
uv sync --locked --extra libs --extra embedded --extra apps --extra qdrant --extra ops
uv run python scripts/check_capstone.py capstones/02_database_bakeoff/starter/project.py --smoke
uv run python scripts/check_capstone.py capstones/02_database_bakeoff/starter/project.py
uv run python scripts/check_capstone.py capstones/02_database_bakeoff/solution/project.py
uv run python capstones/02_database_bakeoff/solution/project.py 
```


## Acceptance criteria

- Run SQLite-vec, Chroma and LanceDB through the shared benchmark contract.
- Implement recommend(rows): reject errors or recall below 0.95, then select the lowest measured p95; return no choice when none qualify.
- Explain deployment, filtering, backup and growth requirements separately from this small local ranking.

The executable contract is [tests](tests/test_02_project.py); [evaluation configuration](evaluation.yaml) identifies entry points. These compact checks are necessary behavioral tests, not complete security or statistical certification. [Rubric](rubric.md) requires the broader measurements and explanation.

## Evidence and limits

See [measured reference results](results/README.md). All three runs are local, 500 rows and 30 queries with three repetitions. Database setup/build costs are separate. This sample cannot predict networked service latency, concurrent write behavior or million-row costs.

## Clean up

Reference sessions remove owned temporary collections. Stop course services with the command in the Tier 5 runbook. Run `python scripts/cleanup.py` to inspect generated cache/data before confirming deletion; keep included fixtures and shared model caches. See [extensions](extensions.md).
