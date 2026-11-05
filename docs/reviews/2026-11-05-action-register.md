# Review action register: Phase 8

Date: 2026-11-05.

| ID | Severity | Status | Owner area | Finding | Evidence | Action | Validation expected | Dependencies |
|---|---|---|---|---|---|---|---|---|
| R-001 | P1 | Completed | Native ingestion | Full catalog upload exceeded server JSON request limit | QdrantStore._put; initial native HTTP 400; [final run](../../results/bonus/capstone-flagship-6f5c96dc.json) | Bound text/photo batches to 128 records, wait for writes, clean failed photo collection | Complete real-server flagship run | Local TLS Qdrant |
| R-002 | P2 | Completed | UI | Default comparison selected another seller's listing and failed | playground/secure_market.py Listing review; [UI result](../../results/bonus/flagship-ui-15d6dc28.json) | Use seller-000's p0000300 default; retain server ownership rejection | All five forms through real HTTPS API | Local identity and TLS server |
| R-003 | P2 | Completed | Measurement | Scratch timing omitted computation of rescored candidate distances | common/research.py rabitq_experiment; [corrected index](../../results/bonus/README.md) | Compute distances inside timer; preserve and label earlier raw files | Native/scratch scripts and notebook rerun | Cached vectors, FAISS |
| R-004 | P2 | Completed | TLS client | Loopback no-keepalive plus localhost fallback added about two seconds per connection | Installed qdrant_remote.py defaults; native.open_client; final API check | Explicit bounded persistent pool and SSL context | Complete native run and all-route regression | Local TLS certificates |
| R-005 | P2 | Completed | Provenance | Original source inventory omitted capstone/TypeScript source | common/bench/hardware.py; [delivery inventory](../../results/bonus/delivery-inventory.json) | Include capstone Python, TS and npm lock; exclude vendor trees | Final inventory/provenance generation | None |
| R-006 | P2 | Deferred | Release verification | Hosted CI has not run and repository has no remote | [Final checklist](../DEFINITION_OF_DONE.md) | Establish intended destination and run existing workflows before hosted-release claim | Ubuntu/Windows/macOS and Linux service jobs | Repository destination and healthy runners |
| R-007 | P2 | Deferred | Documentation access | Nine official/publisher URLs inaccessible to direct checker | [HTTP record](../../results/bonus/online-links.json) | Retry from a permitted network; distinguish DNS/access denial from removed content | Successful retrieval or verified replacement | External network/publisher access |

## Status summary

| Status | Count |
|---|---:|
| Completed | 5 |
| Deferred | 2 |
| Open P0/P1 | 0 |

Additional documented boundaries include single-writer serialized service access, oversized individual records, no power-loss guarantee, fixture-derived app collections, unverified 8 GB minimum and cold-install timing, and partial cleanup-tool coverage. These are not silently converted into production guarantees.
