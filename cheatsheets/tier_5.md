# Tier 5 | Operate and recover

## Identity and isolation

Authenticate a token, derive tenant and role on the server, then AND tenant scope with user filters. Deny unauthorized mutations before database access. Include tenant, model space and index generation in cache identity.

## Durability is a measured boundary

Log before acknowledging writes. Checkpoint with a log watermark and replay after restart. Test abrupt exit and torn tails. A successful process-crash test does not establish power-loss or distributed guarantees.

## Migrate embeddings safely

Create a new space/collection, backfill, replay changes, validate quality and deletion state, switch an alias, then retain a rollback window. Never overwrite an old space merely because the new model has the same dimension.

## Backup and deletion

Define exactly which data a snapshot covers. Keep a deletion ledger and replay it during restore. Measure recovery time and acknowledged writes lost; the course snapshot drill deliberately demonstrates a five-write gap.

## Load and monitoring

Use bounded concurrency, record errors and p95/p99, and distinguish serialized QPS from concurrent throughput. Observe queueing and resource saturation. Inject a process failure and measure recovery rather than hiding failed requests.

## Run and clean up

uv run --extra ops python scripts/prepare_tier5.py
Follow docs/TIER5_RUNBOOK.md for TLS startup and credentials. Run scripts/cleanup.py to preview owned resources before removal. Do not print tokens or use global container prune.
