# Marlowe Search v6 operating runbook

This is a single-worker, local teaching reference. It combines the five Tier 4 flows with trusted seller identities, roles, deletion replay, audit, cache isolation and metrics. Read [Phase 7 evidence](PHASE_7_REPORT.md) for measured limits. Frozen vectors make saved queries offline; arbitrary text, uploaded images or generated answers require the cached models described in [Tier 4 setup](TIER4_APPLICATIONS.md).

## Start the application

```text
uv sync --locked --extra apps --extra ops --extra qdrant --extra notebooks
uv run --no-sync python scripts/prepare_tier5.py
uv run --no-sync python scripts/serve_tier5.py
```

Preparation writes random bearer credentials, random Qdrant keys, a local CA and a 30-day localhost certificate under `.cache/marlowe/tier5/runtime/`. It prints no secrets and changes no system trust store. The runtime directory is mode 0700 on POSIX; the Qdrant metrics token is readable through its specific read-only bind by non-root Prometheus. Protect this ignored directory with your OS account permissions; POSIX mode bits alone do not establish a Windows ACL. Never commit it. The generated CA private key is not retained. To rotate the local certificate, stop clients and replace only the lab TLS material through the preparation workflow; distribute the new CA to the lab clients. For a deployed service use an established certificate lifecycle and secret manager.

The API binds `https://localhost:8443`. Its public `/health` endpoint reports readiness after initialization. Open a second terminal:

```text
uv run --no-sync streamlit run playground/secure_market.py
```

Copy a token from the local `identities.json` into the password field. The UI does not expose a seller selector; the server maps that token to a seller. Two reader accounts represent seller-000 and seller-001, and one administrator represents seller-000. Tokens are local demo secrets, not a user-login, rotation or revocation service. Restart the server to reload changed credentials. The UI calls the authenticated HTTPS API for all data access; its saved text queries omit q005, which belongs to the image-query fixture. The UI displays structured results and does not implement a complete production storefront.

## Trust and deletion boundaries

| Boundary | Enforcement and limitation |
|---|---|
| Authentication | Hash and compare opaque bearer credentials against server-owned identities; no default deployment password |
| Authorization | Reader can read; writer can read/delete; administrator can additionally back up and read metrics |
| Tenant scope | Tenant-owned derived collections plus mandatory AND seller constraint; foreign direct IDs rejected |
| Shared content | Help articles are public marketplace policies, intentionally shared |
| Cache | Tenant, operation, model tag, data generation and full request form the key; deletion clears cached values |
| Migration | Native alias drill is separate from v6 routing; the running API uses fixed model artifacts and must restart when those artifacts change |
| Deletion | Durable deny first, close/rebuild tenant indexes, clear cache, purge owned snapshots containing the listing |
| Backups | API exports tenant primary text collection; image/other derived indexes rebuild using source plus independent deletion history |
| Source | Public immutable teaching fixtures remain unchanged; no claim to delete data from external providers or every storage layer |
| Audit | Allowlisted identifiers and outcome, no raw queries/tokens/vectors; awaited worker-thread fsync JSONL, no tamper-proof remote retention |
| Concurrency | One API worker; in-process locks and ledger do not coordinate multiple workers or hosts |

Do not run multiple application workers against the same deletion ledger. The semaphore limits four admitted operations; HTTP and worker scheduling queues are outside that counter. Native database access bypasses seller authorization: keep it private to the application in a real deployment. Loopback publishing narrows this lab's exposure; local processes still reach it. Transport TLS does not encrypt backups or disk. Use managed volume/backup encryption, restricted keys and appropriate account/network boundaries for sensitive data.

## Native TLS database and monitoring

The separate definition avoids mixing the unsecured beginner profile and the credential-required advanced profile on the same port. Stop an existing port-6333 service first; do not start both profiles.

```text
docker compose --env-file .cache/marlowe/tier5/runtime/compose.env -f docker/compose.tier5.yaml up -d
uv run --no-sync python scripts/checkpoint_tier5.py --native
```

Qdrant uses verified TLS and separate administrator/read-only keys. Prometheus at localhost:9091 scrapes Qdrant over TLS using a protected credential file. Grafana at localhost:3001 provisions the operations dashboard. Its generated admin password is in the ignored compose.env; do not print the interpolated Compose configuration into shared logs. The Qdrant volume is named and owned. Ordinary `down` retains it.

Docker Desktop was not available for execution on the verification host. Equivalent pinned services ran with rootless Podman; the native TLS database and snapshot drills passed. `scripts/monitor_tier5.py` reproduces live TLS scraping and Grafana provisioning in a UUID pod and removes only that pod. `scripts/cluster_tier5.py` does the same for three Qdrant peers and a stopped-peer recovery. These scripts explicitly select the local `podman-machine-default` connection; adapt that engine entry point on another host. The cluster's internal traffic is unencrypted and confined to the lab pod, unlike the separate secure service.

The monitoring drill verifies **database** scraping. API metrics are verified by the load test and captured as `metrics.prom`. `docker/prometheus/tier5-api-local.yml` is an additional configuration for a Prometheus process running on the same host as the API; container localhost does not reach the Windows API. A cross-VM live API scrape was not executed. The Grafana API panels require that additional target and remain empty until it is connected; no dashboard data is fabricated.

## Backup, migration and disaster recovery

1. Record the source watermark, model space, schema, tenant layout and separately protected deletion history. Quiesce writes or establish a consistent snapshot protocol. The native snapshot drill uses a quiesced collection.
2. Export the backup with a checksum. A checksum detects corruption; access controls and an authenticated manifest are separate concerns.
3. Restore into a new collection or process. Replay source writes after the watermark and every later deletion **before** serving requests. The lesson deliberately omits five post-backup writes to demonstrate measurable data loss.
4. Validate counts, tenant ownership, deleted IDs, model-space compatibility and representative queries. Switch application routing only after those gates pass.
5. For a model migration, build green in its own space, replay writes/deletes into both generations, evaluate relevance and errors, and coordinate encoder plus collection publication. A native alias change is atomic at the database, but application caches and encoder workers need their own coordinated generation.
6. Keep blue available for a bounded rollback window. Delete withdrawn records from both generations and handle backup retention. Roll back both routing and encoder if gates fail.

`scripts/checkpoint_tier5.py` measures fresh-process restore, atomic route publication followed by process exit, compaction and cache behavior. Its five-write loss is a workload-specific RPO observation, not a universal promise. Its restore timer excludes operator response and external traffic switching. If the data backup and deletion ledger fail together, the demonstrated protection does not apply. Test that independent failure domain before deployment.

## Load and operational alarms

```text
uv run --no-sync python scripts/load_tier5.py
uv run --no-sync python scripts/cluster_tier5.py
uv run --no-sync python scripts/monitor_tier5.py
```

The load script owns an HTTPS API on port 8444, uses valid frozen text queries for two sellers, varies concurrency, terminates only its owned child, restarts it and records errors and readiness time. It never changes the credentials. Allow port 8444 to be free; the original 8443 service can remain running. An interrupted benchmark is a failure exercise, not an availability estimate.

Watch error rate, rejected admissions, tail latency, request rate, free disk, process/server memory and index readiness. Prometheus exposes route templates instead of raw IDs and omits tenant labels to limit sensitive data and label cardinality. Begin with application-specific targets; do not copy the laptop's numbers into an SLO. Load evidence includes overload failures and the single-worker throughput limitation. Investigate audit fsync cost, request scheduling and the shared lock before attributing all latency to vector search.

## Sensitive data and retention

Minimize metadata before indexing; avoid raw identifiers or private text unless retrieval requires them. Embeddings are not guaranteed anonymization. [Morris and colleagues](https://arxiv.org/abs/2310.06816) demonstrate text reconstruction and sensitive-information recovery under particular model and attack conditions; this does not imply universal recovery of every embedding. Restrict vector exports and backups as well as source text. The course uses synthetic marketplace data and does not reproduce an inversion attack.

Deletion policy must cover live collections, blue/green generations, caches, logs, exports, backup expiry and independent deny history. A backup retention requirement may prevent immediate byte removal; document that policy and prevent serving deleted data after restore. The course's owned snapshots can be purged immediately, while immutable public fixtures remain. This is a technical demonstration, not a legal-compliance certification.

## Stop and clean up

Stop the API/UI with Ctrl+C. For the advanced Compose stack:

```text
docker compose --env-file .cache/marlowe/tier5/runtime/compose.env -f docker/compose.tier5.yaml down
uv run python scripts/cleanup.py
```

The cleanup command previews resources and requests a selection. Do not remove a deletion ledger while retaining backups that could resurrect its records. Never use a global prune for this course. Native drills remove only UUID collections and pods they created.
