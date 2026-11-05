# Ship a complete Marlowe Search demo

Prerequisites: Tiers 1–5. Budget: one afternoon for the baseline, longer for the measurements and extensions. Use Python 3.12 and the repository's locked environment. Work from the repository root.

## User stories

- As a shopper, I can use semantic, keyword/filtered and multilingual search, see recommendations and duplicates, ask help questions, and search by photo.
- As a seller, I can use the API and UI with authenticated tenant scope.
- As an operator, I can inspect metrics, restore a database snapshot and measure the recovery gap.

## Build and run

1. Run the starter smoke command below. The starter is a small working baseline, not a finished submission.
2. Read [architecture](architecture.md), then fill the `YOUR CODE HERE` work in `starter/project.py`. Keep the exported contract named in the acceptance tests.
3. Run acceptance against your file. Inspect the reference only after attempting the contract.
4. Run the measured reference and write your own decision with raw evidence.

```sh
uv sync --locked --extra libs --extra embedded --extra apps --extra qdrant --extra ops
uv run python scripts/check_capstone.py capstones/05_marlowe_search/starter/project.py --smoke
uv run python scripts/check_capstone.py capstones/05_marlowe_search/starter/project.py
uv run python scripts/check_capstone.py capstones/05_marlowe_search/solution/project.py
uv run python capstones/05_marlowe_search/solution/project.py --backend qdrant-secure --operations
```

Before the native command, follow [TLS preparation and service startup](../../docs/TIER5_RUNBOOK.md). The plain Qdrant profile must release port 6333. The reference's load/monitoring helpers use rootless Podman on the verified host. For an offline first run, omit native/operations flags and choose `--backend tinyvec`.

## Acceptance criteria

- Evaluate search, RAG, recommendations/deduplication and photo retrieval against the chosen backend.
- Run the secure API and Streamlit UI with the same identity file and TLS database.
- Verify the backup/deletion/migration drills, inspect the monitoring dashboard, and explain the observed five-write recovery gap.

The executable contract is [tests](tests/test_05_project.py); [evaluation configuration](evaluation.yaml) identifies entry points. These compact checks are necessary behavioral tests, not complete security or statistical certification. [Rubric](rubric.md) requires the broader measurements and explanation.

## Evidence and limits

See [measured reference results](results/README.md). The demo rebuilds owned derived collections from immutable course fixtures when a session starts and removes its collections on close. It is not a persistent live-catalog ingestion service. Help articles are shared public fixtures. Backup scopes and the deletion ledger are explained in the Tier 5 runbook.

## Clean up

Reference sessions remove owned temporary collections. Stop course services with the command in the Tier 5 runbook. Run `python scripts/cleanup.py` to inspect generated cache/data before confirming deletion; keep included fixtures and shared model caches. See [extensions](extensions.md).

## Launch the API and UI

After TLS preparation, start the chosen database/monitoring services with `docker compose --env-file .cache/marlowe/tier5/runtime/compose.env -f capstones/05_marlowe_search/compose.yaml up -d`. In separate terminals, run:

```sh
uv run --extra apps --extra qdrant python capstones/05_marlowe_search/solution/serve.py
uv run --extra apps streamlit run capstones/05_marlowe_search/solution/ui.py
```

Copy your local identity token from the private runtime file into the password field; never paste it into reports or screenshots. The demo form defaults use seller-000 listing IDs. Other sellers must enter their own IDs. `python scripts/verify_flagship_ui.py` exercises all five forms against an owned HTTPS API and the real TLS database. Use the runbook's shutdown command for this same Compose project.
