# Tier 5 checkpoint: operate Marlowe Search v6

Complete Modules [21](../../modules/21_operations/README.md), [22](../../modules/22_performance/README.md) and [23](../../modules/23_security_reliability/README.md). Use the [runbook](../../docs/TIER5_RUNBOOK.md) and [memory worksheet](../../docs/MEMORY_MATH.md).

```text
uv run python scripts/checkpoint_tier5.py
uv run --extra apps --extra qdrant --extra embedded pytest tests/test_tier5.py
```

For the explicit native extension, prepare TLS and start the secure service, then run:

```text
uv run --extra qdrant python scripts/checkpoint_tier5.py --native
uv run --extra apps python scripts/load_tier5.py
uv run --extra qdrant python scripts/cluster_tier5.py
uv run --extra ops python scripts/monitor_tier5.py
```

## Acceptance evidence

| Requirement | Evidence to submit |
|---|---|
| Retry safety | Duplicate replay leaves unique live IDs; pending batch high-water stays bounded |
| Index maintenance | Identical live view before/after compaction; native bytes before DELETE and after VACUUM |
| Migration | Both model spaces, deletion replay, successful alias switch, wrong-space rejection and rollback |
| Backup/restore | Verified snapshot, fresh-process restore, deletion absent, lost acknowledged writes and measured restoration time |
| Tenant isolation | Missing/bad identity, hostile filter, foreign direct IDs, all private query branches and cache separation tested |
| Deletion | Derived index eviction, cache invalidation, owned snapshot purge and restart behavior |
| Capacity | Payload, graph, metadata, replica/headroom terms and explicit excluded peaks |
| Performance | Development-only tuning, held-out recall, sample count, load p50/p95/p99, throughput and errors |
| Replication | Real peer stop/rejoin, acknowledged records recovered; simulator labeled separately |
| Monitoring | Real TLS scrape, provisioned dashboard, metric definitions and unverified target gaps |
| Cost | Transparent compute/storage/request/egress/labor assumptions; no-server alternative |

The [reference evidence](../../results/tier5/README.md) includes a nonzero restore gap and overload failures. Passing the checkpoint means demonstrating and explaining the boundaries, not hiding adverse results. The [Phase 7 report](../../docs/PHASE_7_REPORT.md) lists executed checks and limits. Bonus modules and full capstone packages arrive in Phase 8.
