# A cited help assistant

Prerequisites: Tier 4, Module 18. Budget: one afternoon for the baseline, longer for the measurements and extensions. Use Python 3.12 and the repository's locked environment. Work from the repository root.

## User stories

- As a shopper, I receive a source citation with a help answer.
- As a support owner, I can see abstentions and retrieve the underlying passage for review.

## Build and run

1. Run the starter smoke command below. The starter is a small working baseline, not a finished submission.
2. Read [architecture](architecture.md), then fill the `YOUR CODE HERE` work in `starter/project.py`. Keep the exported contract named in the acceptance tests.
3. Run acceptance against your file. Inspect the reference only after attempting the contract.
4. Run the measured reference and write your own decision with raw evidence.

```sh
uv sync --locked --extra libs --extra embedded --extra apps --extra qdrant --extra ops
uv run python scripts/check_capstone.py capstones/03_rag_assistant/starter/project.py --smoke
uv run python scripts/check_capstone.py capstones/03_rag_assistant/starter/project.py
uv run python scripts/check_capstone.py capstones/03_rag_assistant/solution/project.py
uv run python capstones/03_rag_assistant/solution/project.py --backend sqlite-vec
```


## Acceptance criteria

- Implement HelpProject with ask(question_id, generate=False) and close().
- Return cited source excerpts by default; reject unknown saved question IDs and abstain when no passage clears the documented threshold.
- Evaluate all saved questions, record passage recall, and manually assess answer correctness separately from citation existence.

The executable contract is [tests](tests/test_03_project.py); [evaluation configuration](evaluation.yaml) identifies entry points. These compact checks are necessary behavioral tests, not complete security or statistical certification. [Rubric](rubric.md) requires the broader measurements and explanation.

## Evidence and limits

See [measured reference results](results/README.md). The default is an extractive answer, not an LLM completion. A correct citation may cite the wrong policy. The 0.35 threshold is illustrative and needs development-set calibration. --generate explicitly uses local Ollama and the pinned model; see the Tier 4 guide.

## Clean up

Reference sessions remove owned temporary collections. Stop course services with the command in the Tier 5 runbook. Run `python scripts/cleanup.py` to inspect generated cache/data before confirming deletion; keep included fixtures and shared model caches. See [extensions](extensions.md).
