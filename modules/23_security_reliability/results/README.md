# Module 23 results

Read the [measured Tier 5 tables and raw records](../../../results/tier5/README.md). The [Phase 7 report](../../../docs/PHASE_7_REPORT.md) records executed checks and limitations.

Reproduce the local checkpoint with `uv run python scripts/checkpoint_tier5.py`; add `--native` only after secure database setup. Load, cluster and monitoring use the explicit commands in the [runbook](../../../docs/TIER5_RUNBOOK.md). Diagnostic timings have different scopes and must not be ranked together.
