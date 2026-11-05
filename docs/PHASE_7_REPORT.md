# Phase 7 delivery and verification

Phase 7 delivers **Tier 5, Modules 21–23, and Marlowe Search v6**. All 24 core lessons are now available. The repository version is 0.7.0; the lock resolves 276 packages, with cryptography 50.0.2 explicitly exposed through the `ops` extra. Phase 8 remains the bonus modules, full capstone packages and final course audit.

## Delivered components

- [Operations](../modules/21_operations/README.md): collection/tenant design, stable identity, bounded ingestion, idempotent replay, tombstones, compaction, model migration, native aliases and snapshot restore.
- [Performance](../modules/22_performance/README.md): capacity, held-out target tuning, replication/sharding, cache, real Locust load, Prometheus/Grafana, cost assumptions and the no-server option.
- [Security and reliability](../modules/23_security_reliability/README.md): trusted identities, roles, verified TLS, negative tenant tests, minimized audit, embedding disclosure overview, deletion and recovery.
- Twelve example scripts, three Marlowe use cases, nine runnable starters with solutions and acceptance checks, eighteen hidden quiz answers, three cleared notebooks, and sixteen executed feature profiles.
- [Secure operating runbook](TIER5_RUNBOOK.md), [memory/cost worksheet](MEMORY_MATH.md), [Tier 5 checkpoint](../checkpoints/tier5/README.md), raw results and a generated load plot.

The v6 API wraps product search, public help, similar items, duplicate review and photo search. A server-owned credential maps to seller and role. Private derived indexes are tenant-scoped; product search additionally applies a mandatory tenant predicate. The cache includes tenant and data generation, and deletion persists a deny decision before invalidating indexes, cache and owned snapshots. A companion Streamlit UI calls the authenticated HTTPS API.

Shared changes preserve v5 defaults while allowing empty tenant collections, scoped multilingual/photo artifacts and portable SQLite backup exports. The cleanup preview now recognizes both explicitly named course Compose projects. A separate advanced Compose definition requires credentials and TLS, keeping it distinct from beginner services on the same ports.

## Executed checks

| Check | Observed outcome |
|---|---|
| Full offline regression suite | **244 passed**, 11 opt-in tests deselected |
| Base-only environment | **177 passed**, 67 optional tests skipped, 11 deselected |
| API regression after moving audit I/O off the event loop | **25 passed**, including earlier v5 flows |
| New lesson/use-case execution | **15 scripts passed**, with a scoped retry after the tied-result assertion correction |
| Notebooks | **3 executed, 18 code cells**; committed sources remain cleared |
| Native notebook coverage | Secure Qdrant cells executed; cluster/load/monitoring notebook cells skipped by profile, with their standalone scripts executed separately |
| Structure | All **24 modules** pass the 17-section, quiz, runnable metadata and notebook checks |
| Included artifacts | All **337** committed data/model-vector artifacts verified |
| Native server experiments | Qdrant TLS/auth, real alias migration/rollback and snapshot restore executed |
| Distributed experiment | Three real peers, two shards, three replicas, write consistency two, peer stop/rejoin and post-recovery majority read executed |
| Load | Real HTTPS requests at 1/8/32 users and an owned API process interruption; adverse results retained |
| Monitoring | Prometheus authenticated TLS scrape, 26 observed database series, Grafana provisioning with four panels |
| Static checks | Ruff lint/format, local Markdown links and secure Compose configuration validation |

The full suite includes negative isolation and deletion checks on TinyVec, SQLite-vec and Qdrant local. The secure UI test verifies all five forms remain gated until a token is supplied. API endpoint tests cover authenticated operation; a complete browser interaction against the authenticated UI was not performed.

Execution details are preserved in [the initial script report](../results/tier5/execution-b186cce9.json) and [the corrected security-module report](../results/tier5/execution-3c1889f2.json). Later changes to audit scheduling and native read-consistency placement were rerun through their standalone load/cluster scripts; their latest records are linked from the [derived results](../results/tier5/README.md). The final local validation inventory is [recorded separately](../research/phase7-validation.json).

## Observed results and corrected assumptions

The [measured tables](../results/tier5/README.md) derive from append-only JSON and CSV files. Hardware, installed package versions, source hashes and commands accompany successful runs. The host is Windows with Python 3.12, approximately 31 GiB RAM and 24 logical cores; containers ran through the working rootless Podman connection. Timing scopes differ and are not combined into a database ranking.

- **Idempotence and compaction:** replay leaves 1,000 unique IDs, with at most two pending batches. Scratch compaction reduces 2,000 physical versions to 900 live rows without changing the live view. SQLite file size stays 8,220,672 bytes after DELETE and becomes 2,056,192 after VACUUM.
- **Restore:** a fresh process restores 99 records after applying a newer deletion ledger. Five acknowledged post-backup writes are intentionally lost; no deleted record is resurrected. The native 1,665,536-byte Qdrant snapshot restores 499 points after a deletion. Timings are in the raw records and exclude operator response and traffic switching.
- **Model migration:** 500 MiniLM and Qwen vectors live in separate model spaces. Both generations receive the deletion, the native alias switches and rolls back, and an incompatible query is rejected. The application router separately demonstrates atomic collection/encoder publication and process-exit recovery. This is not a full automatic online migration coordinator.
- **Tuning:** development queries select nprobe=4. Held-out recall@10 is 1.000 on ten distinct queries repeated three times. These small synthetic data do not establish broad relevance or stable tail-latency guarantees.
- **Load:** the final run completed 207 requests with one user and no failures, at 10.80 requests/second and p95 55 ms. At eight users, five of 225 completed requests failed; at 32 users, p95 rose to 3,200 ms. The interrupted run had twelve failures out of 161. High concurrency is still a documented limitation, not a claimed production SLO.
- **Audit scheduling:** load exposed blocking fsync work in the async request loop. Audit writes now run in a worker thread and are awaited before a response returns. Request timing includes audit wait. A short metrics timeout also failed after a saturated run; the bounded collection timeout was extended while retaining the incomplete CSV/log evidence.
- **Consistency:** corrected native requests pass read consistency as an HTTP query parameter. The immediate majority read returned 500 while a peer was down; consistency=1 returned both records. Majority reads returned both after recovery, with no acknowledged data loss. Earlier records placed consistency in the body and cannot support a majority-read claim. This transient result is not a universal statement about steady-state majority availability.
- **Validation corrections:** an image-query fixture was initially sent to text search; the final workload excludes it. A tied-score test incorrectly required fixed native result order; it now checks membership. Tests also caught empty photo collection handling and SQLite's native snapshot format, both fixed before final verification.

## Limits and handoff

This is a single-worker reference with in-process locks, fixed frozen model artifacts and immutable public source fixtures. It does not implement distributed identity management, cross-process deletion coordination, arbitrary catalog mutation, automatic credential rotation, encrypted disk storage or a complete retention service. Deleting public course fixtures is intentionally outside the application deletion boundary. Help-center content is public and shared. Database-wide read keys do not enforce seller ownership.

The ten-million-vector memory budget and hosting costs are calculations with explicit assumptions, not a measured deployment or provider quote. Replicas run on one host, not separate failure zones. Native server memory was not sampled. Very short load runs have limited tail evidence and retain startup effects. The independently durable deletion ledger is an assumption of the recovery drill; losing it with the backup invalidates the demonstrated protection.

Live database scraping and dashboard provisioning were verified. API metrics were captured by the load runner, while cross-VM live API scraping and rendered dashboard interaction were not executed. A same-host API scrape configuration is supplied. Docker Compose syntax was validated; equivalent pinned services ran under Podman, not Docker Desktop. Hosted CI and the added secure-operations job were not run locally. No cloud service, paid API, model download, Git commit or repository publication occurred in this phase.

Temporary cluster and monitoring pods remove themselves. The remaining dedicated verification database and API are stopped after checks, with cleanup recorded in the validation inventory. Cached model weights and unrelated resources remain. Continue with Phase 8 for the finishing deliverables.
