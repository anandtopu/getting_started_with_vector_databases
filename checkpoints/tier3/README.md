# Tier 3 checkpoint · compare databases for Marlowe

Run the same catalog workload on at least four databases, then recommend one for a stated application need. The four embedded engines are sufficient to complete the minimum locally. Server examples add native hybrid, tenant, snapshot and consistency comparisons. Allow 45–90 minutes after Modules 11–16.

## Run the shared workload

Install the embedded extra and run the comparison from the repository root.

```sh
uv run --extra embedded python scripts/checkpoint_tier3.py --output .cache/marlowe/tier3/checkpoint
```

This runs Chroma, LanceDB, SQLite-vec and DuckDB. To add a running server, install its client extra and name its backend. For example:

```sh
docker compose -f docker/compose.yaml --profile qdrant up -d
uv run --extra qdrant python scripts/check_profile.py qdrant
uv run --extra qdrant python scripts/checkpoint_tier3.py --backends qdrant --output .cache/marlowe/tier3/checkpoint
```

Use the same output directory to combine raw reports, leaderboard rows and plots. The reference workload has 500 products and 50 held-out queries, with k=10, twenty warm-ups and five repetitions. Every request uses included MiniLM vectors. The independent reference scores the same eligible rows.

## Prepare the decision

| Include | What the reviewer checks |
|---|---|
| Requirement | State a recall floor, p95 budget, query mix and operational need before choosing the winner. |
| Matched runs | Dataset, query and embedding hashes, metric, k, concurrency and hardware agree. |
| Retrieval quality | Neighbor recall and judged relevance are both reported. |
| Cost | p50/p95, repeated QPS, insertion/build, client RSS and logical snapshot size have clear boundaries. |
| Correctness | Update, delete, typed filters and a fresh-resource restore work. |
| Native feature | Show one field filter, hybrid query, snapshot or consistency result through the database’s API. |
| Recommendation | Explain which requirement makes the chosen engine appropriate and which observed cost you accept. |
| Reproduction | Link exact commands, raw JSON, versions and runtime limits. |

The portable comparison constructs eligible ID sets from session metadata and sends them into native search. Report that cost and behavior. Native scripts test each engine’s field predicates separately. The Python RSS sampler measures the client process. Server-container memory is recorded separately when available.

Use the Playground’s **Databases** tab to send the same saved query and selected price/region filter to several running engines. The tab creates private experiment collections and closes them after the comparison.

## Reference and self-check

Read the [reference results and recommendation](results/README.md). Eleven of twelve measured systems reproduced all exact neighbors on the reference workload. The initial Elasticsearch approximate configuration reached 0.854. A low latency row is useful only if it meets the required quality.

You are ready to move on when you can explain a database’s native record model, distinguish a logical export from a native backup, detect search-index visibility lag, interpret a query plan or index-build state, and defend your database choice using the observed workload.

Stop each profile after use with `docker compose -f docker/compose.yaml --profile PROFILE down`. Use the course cleanup preview before removing retained volumes.
