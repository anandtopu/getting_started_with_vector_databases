# Operate isolated seller search

Prerequisites: Tier 5. Budget: one afternoon for the baseline, longer for the measurements and extensions. Use Python 3.12 and the repository's locked environment. Work from the repository root.

## User stories

- As a seller, I can search only my listings even when a request contains an adversarial filter.
- As an administrator, I can delete a listing, restart, and verify it stays deleted.

## Build and run

1. Run the starter smoke command below. The starter is a small working baseline, not a finished submission.
2. Read [architecture](architecture.md), then fill the `YOUR CODE HERE` work in `starter/project.py`. Keep the exported contract named in the acceptance tests.
3. Run acceptance against your file. Inspect the reference only after attempting the contract.
4. Run the measured reference and write your own decision with raw evidence.

```sh
uv sync --locked --extra libs --extra embedded --extra apps --extra qdrant --extra ops
uv run python scripts/check_capstone.py capstones/04_multitenant_search/starter/project.py --smoke
uv run python scripts/check_capstone.py capstones/04_multitenant_search/starter/project.py
uv run python scripts/check_capstone.py capstones/04_multitenant_search/solution/project.py
uv run python capstones/04_multitenant_search/solution/project.py --backend qdrant-secure --native
```

Before the native command, follow [TLS preparation and service startup](../../docs/TIER5_RUNBOOK.md). The plain Qdrant profile must release port 6333. The reference's load/monitoring helpers use rootless Podman on the verified host. For an offline first run, omit native/operations flags and choose `--backend tinyvec`.

## Acceptance criteria

- Implement scenario(root, backend) and enforce trusted identity, roles and mandatory tenant scope.
- Reject reader mutations, purge affected backup snapshots and preserve deletion across restart.
- Run the native alias migration/restore and TLS API load drills; report failures and downtime as measurements.

The executable contract is [tests](tests/test_04_project.py); [evaluation configuration](evaluation.yaml) identifies entry points. These compact checks are necessary behavioral tests, not complete security or statistical certification. [Rubric](rubric.md) requires the broader measurements and explanation.

## Evidence and limits

See [measured reference results](results/README.md). The test role is assigned by the server; request parameters cannot establish identity. The load drill intentionally includes process failure and uses TinyVec behind the TLS API; the native migration drill separately uses TLS Qdrant. Neither proves distributed transaction isolation.

## Clean up

Reference sessions remove owned temporary collections. Stop course services with the command in the Tier 5 runbook. Run `python scripts/cleanup.py` to inspect generated cache/data before confirming deletion; keep included fixtures and shared model caches. See [extensions](extensions.md).
