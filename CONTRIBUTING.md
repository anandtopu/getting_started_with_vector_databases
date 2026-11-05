# Contributing

Start from [PLAN.md](PLAN.md) and the [feature map](docs/FEATURE_MAP.md). Work on one lesson, fix, or experiment at a time. Describe the learner-visible problem and show the verifying command.

Use Python 3.12 and `uv sync --locked`. Before submitting:

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/run_all_examples.py
uv run python scripts/check_links.py
```

Use `uv run --extra embedded pytest` for embedded tests. Default tests block Python network sockets and never download models. LanceDB's event-loop test permits only loopback connections for its internal socketpair. Native libraries are not covered by Python socket blocking; disable their telemetry and automatic downloads explicitly.

Examples start with commands, expected output, prerequisites, and CPU time estimates. Use common embedding helpers, shared stores for portable comparisons, and `common.pretty`. Keep native API demonstrations explicit about engine-specific behavior. No empty adapters or invented benchmark rows.

Add regression tests for behavior changes. Preserve raw measurements; record dataset and metric changes. Keep incomparable workloads separate. Never commit credentials, weights, bulk generated data, notebook outputs, or private data.

Dependency changes need a fresh lock, official documentation checks, updated verification notes, and `uv run python scripts/export_requirements.py`. Run model/Docker checks explicitly and report unavailable checks. Local tests are not a remote CI pass.

Use issue/PR templates when hosted on GitHub. Hosting is not configured in this checkout. Use a private reporting channel for security-sensitive reports when available; do not post secrets publicly.
