# Cross-file Integration Checks: Phase 8

Date: 2026-11-05. Pass 2 follows the [individual file pass](2026-11-05-per-file-analysis.md).

## Flow checks

| Flow | Files checked | Status | Evidence | Gap/risk | Action |
|---|---|---|---|---|---|
| Exported vectors to official TS clients | prepare_bonus.py, common/bonus.py, B1 src/contract.ts and native.ts, npm lock, lesson/notebook | Pass | Both real clients upsert/replace/filter/delete 200 vectors; strict compile and two Node tests | Not a production credential/tenant boundary | Keep fixture identity and explicit setup |
| Mutation to WAL to restart | service.py, durable.py, wal.py, core tests and B2 examples | Pass within scope | Four callers/20 sequences; os._exit recovery; truncated tail; corrupt full record rejection | One process and serialized access; no power-cut or log-retention policy | Bound claims in lesson |
| Public benchmark source to held-out result | download_benchmarks.py, manifest, research.py, B3 notebook and raw records | Pass within scope | Checksummed licensed subset; 60/60 query split; 0.970 held-out recall | Laptop protocol reproduction, not paper-scale replication | Preserve sampling/timing definitions |
| RaBitQ estimator to reported latency | rabitq.py, research.py, B4 exercises, native FAISS factory, plot | Pass after R-003 | Candidate distances recomputed in timer; seed results and byte accounting agree | Different native/scratch scopes; full vectors retained | Supersede early timings explicitly |
| Secure API to real database | secure_api.py, secure_market.py, AppDatabase, native.open_client, QdrantStore | Pass after R-001/R-004 | Native all-route/isolation/restart regression; complete flagship evaluation | No distributed-worker guarantees | Keep native regression in CI |
| Product/photo bulk ingestion | QdrantStore._put, MultimodalSearch._put_native, full flagship | Pass after R-001 | Initial roughly 150 MB request rejected; final 128-row batches completed | Per-record size is not bounded by row count | Document oversized-record boundary |
| Identity to UI comparison | secure_market UI, secure API, seller fixture, flagship UI verifier | Pass after R-002 | All five UI forms now return data; foreign ownership tests still reject | Defaults target seller-000 only | Other identities enter owned IDs |
| Backup/migration/deletion | native.py, drills.py, secure_market.py, capstones 04/05 | Pass within scope | Native 499-row restore; zero resurrected deletions; separate five-write loss retained | Deletion ledger survives independently; public fixtures remain | Preserve recovery assumptions |
| Monitoring/load to operational report | load_tier5.py, monitor_tier5.py, capstone references | Pass as experiments | Real Locust failures/recovery, Prometheus scrape, Grafana provisioning | Not a passing production SLO; dashboard browser interaction unrun | Keep negative results visible |
| Lesson/config/result navigation | feature map, feature runner, notebook runner, link checker, delivery audit | Pass locally | 28 lesson packages, 72 diagnostic profiles, ten mapped retrieval configs | Historical native evidence not rerun wholesale in Phase 8 | Link exact evidence and phase |
| Source to provenance | hardware.py, npm lock, capstone sources, delivery inventory | Pass after R-005 | Current inventory hashes lesson/capstone sources; new provenance includes TS/lock | Older immutable records have narrower hashes | Retain original records, label boundary |
| CI/config to deployment | CI workflows, Compose include, native helpers | Partial | Local Compose parse and equivalent rootless Podman services | Hosted CI and literal Docker startup unavailable | Run on intended remote/healthy Docker host |

## Contract checks

| Contract | Producer | Consumer | Status | Notes |
|---|---|---|---|---|
| Vector dimensions/model space | Frozen manifests and Python exporter | TS validation, collection specs, app sessions | Pass | Explicit vectors; incompatible spaces reject |
| Durable acknowledgement | WAL append/fsync sequence | HTTP response and replay watermark | Pass within process-crash scope | An unacknowledged operation may still replay; retry semantics documented |
| Trusted tenant and role | Keyring identity | Mandatory scope, cache, mutation guards | Pass | User-supplied tenant fields cannot establish identity |
| Search result identity | Native point IDs plus adapter catalog | API serializers and UI | Pass | Stable business IDs survive database boundaries |
| Evidence timing scope | Experiment implementation | Result index, plots and report | Pass after correction | Early RaBitQ timing records explicitly superseded |
| Optional dependency/profile markers | Example headers | General/notebook/bonus runners | Pass | Missing optional requirements are skips, not passes |

## Integration findings

Confirmed defects and fixes are in the [action register](2026-11-05-action-register.md). No P0 or unresolved P1 issue was observed in the reviewed teaching scope. That statement does not certify a production deployment or third-party dependency security. The hosted-CI and external-reachability gaps remain facts; predictions about scale or a different host remain unverified.
