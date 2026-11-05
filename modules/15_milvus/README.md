# Module 15: Milvus schemas, indexes and consistency

> After this module you can distinguish an acknowledged write, a visible product and a fully built vector index.

**Time:** ~150 minutes · **Level:** Intermediate · **Needs:** 16 GB system RAM recommended, about 6 GB free disk, Docker profile milvus (etcd, MinIO and Milvus). **Downloads:** initial package and container installation need network access. The core workload uses the included product and query vectors. 

**TinyVec v5 and Marlowe Search v1.** The catalog now runs through a native database. [Measured results](results/README.md).

## Prerequisites

Complete [Module 14](../14_weaviate/README.md) and the [Tier 2 checkpoint](../../checkpoints/tier2/README.md). Run all commands from the repository root. Use the [database terminology table](../../docs/TERMS_ACROSS_DATABASES.md) for new terms and the [setup guide](../../docs/SETUP.md) for port and connection settings.

Start the local profile with `docker compose -f docker/compose.yaml --profile milvus up -d`. Check it with `docker compose -f docker/compose.yaml --profile milvus ps`. Allow the service to become ready before connecting the client.

## Learning objectives

- Distinguish an acknowledged write, a visible product and a fully built vector index.
- Trace a product ID through a native write, query and restore.
- Measure eligible-neighbor recall, judged relevance and p95 retrieval latency.
- Explain which operational requirement would change your database choice.

## The big idea

A warehouse can accept a delivery before every shelf label has been updated. In Milvus, insert acknowledgement, search visibility, flushing a segment, index build and loading the index are different events. If a lesson times the wrong event, it can say a disk index is ready while all its rows are still waiting to be indexed.

## How it works

```mermaid
flowchart LR
    n0["Insert product and partition key"] --> n1["Acknowledge write"] --> n2["Flush sealed segment"] --> n3["Build and load index"] --> n4["Read at consistency level"]
```

A collection schema fixes its primary key and vector fields. A partition key routes related records into partitions. Segments hold batches of rows. The index describes how a vector field is searched, and the consistency policy determines which writes a read must observe. Strong reads wait for an appropriate visibility point; a session read is designed to include the client’s own writes. Eventual consistency permits lag.

## Build it yourself

Construct a two-revision inventory record. Read at the same requested time with two different applied watermarks. The older reader still sees a sale, while the caught-up reader sees a retired listing. This simulator isolates the idea; the native experiment separately measures actual server visibility under different policies. Start with the [scratch example](examples/01_from_scratch.py). Predict its result, change one input, then explain why the output changed.

## Now in a real database

The MilvusClient example creates an explicit schema and IVF flat index. The hybrid example configures a text analyzer and a BM25 function that writes to a sparse field, then fuses dense and sparse candidates with RRFRanker. The DISKANN example flushes 4,096 real product vectors and checks indexed_rows before loading and querying. A finished status with pending rows is insufficient evidence. For portable predicates the comparison computes eligible IDs from session metadata and supplies them to the native query before taking k. The native scripts also exercise field filters directly. Logical snapshots read rows back from the database before writing a portable snapshot. Native backups are marked separately.



## Walkthrough

| Example | Run | Expected observation |
|---|---|---|
| [01_from_scratch](examples/01_from_scratch.py) | `uv run python modules/15_milvus/examples/01_from_scratch.py` | stale and current revisions |
| [02_production](examples/02_production.py) | `uv run --extra milvus python modules/15_milvus/examples/02_production.py` | IVF collection and native result |
| [03_measure](examples/03_measure.py) | `uv run --extra milvus python modules/15_milvus/examples/03_measure.py` | three index families |
| [04_hybrid_bm25](examples/04_hybrid_bm25.py) | `uv run --extra milvus python modules/15_milvus/examples/04_hybrid_bm25.py` | BM25 and dense RRF |
| [05_partitions_consistency](examples/05_partitions_consistency.py) | `uv run --extra milvus python modules/15_milvus/examples/05_partitions_consistency.py` | partition and consistency observations |
| [06_disk_index](examples/06_disk_index.py) | `uv run --extra milvus python modules/15_milvus/examples/06_disk_index.py` | 4,096 indexed disk rows |

The [notebook](notebook.ipynb) mirrors the example scripts. Its server cells check `MARLOWE_NOTEBOOK_PROFILES`. Set that environment variable to a comma-separated list of running profiles before starting Jupyter. Standalone scripts use the indicated local service directly.

## Measure it

Run `uv run --extra milvus python modules/15_milvus/examples/03_measure.py` for the shorter lesson experiment. For the common workload use `uv run --extra milvus python scripts/checkpoint_tier3.py --backends milvus`. The published comparison uses 500 products, 50 held-out queries, k=10, twenty warm-ups and five repetitions. Compare with the matched exact SQLite or DuckDB row. Tier 2’s 1,000-product experiments have different inputs. [Module results and figures](results/README.md) · [Central leaderboard](../../results/leaderboard.md).

## When to use it, and when not to

Milvus is a candidate when the required index families, partitioning or hybrid retrieval justify a service with multiple components. Its standalone Compose profile includes etcd and object storage. Measure consistency and build time at realistic segment sizes; a tiny growing segment may use a different path.

## Real-world use case

A seller withdraws the product that ranked first. With strong consistency, delete it, repeat the query and verify that the withdrawn ID is absent. A separate read-after-write example records what actually happened for Eventually, Session and Strong rather than promising that every eventual read is stale. [Use-case script](use_case/retired_listing.py).

```sh
uv run --extra milvus python modules/15_milvus/use_case/retired_listing.py
```

## Common mistakes

- A field named key returns key in this client version. Read the declared primary-key name.
- A loaded collection can have pending index rows. Inspect both indexed_rows and pending_index_rows.
- Retrieving BM25 results requires an analyzer, sparse output field and BM25 index. Create them together.
- A partition key routes data but does not authenticate a tenant. Enforce authorization before constructing the query.

## Exercises

### Practice · Find a visible product revision

Return the value of the highest revision at or below the reader's watermark. For inputs `[[[4,"gone"],[1,"sale"]],2]`, expect `"sale"`. Edit the [starter](exercises/01_practice.py), run its check and compare with the [solution](solutions/01_practice.py).

```sh
uv run python scripts/check_exercise.py modules/15_milvus/exercises/01_practice.py
```

### Apply · Route a partition-key lookup

Return only the partitions whose routing metadata includes the tenant. For inputs `[{"b":["south"],"a":["north"]},"north"]`, expect `["a"]`. Edit the [starter](exercises/02_apply.py), run its check and compare with the [solution](solutions/02_apply.py).

```sh
uv run python scripts/check_exercise.py modules/15_milvus/exercises/02_apply.py
```

### Stretch · Confirm that an index finished building

Require a finished state and coverage of the expected sealed rows before claiming an index build. For inputs `["Finished",50,100]`, expect `false`. Edit the [starter](exercises/03_stretch.py), run its check and compare with the [solution](solutions/03_stretch.py).

```sh
uv run python scripts/check_exercise.py modules/15_milvus/exercises/03_stretch.py
```

## Quiz

1. What is a sealed segment?

<details><summary>Answer</summary>

A closed batch that can proceed through index construction.

</details>

2. What does a partition key control?

<details><summary>Answer</summary>

Routing into physical partitions, subject to the configured partition count.

</details>

3. Which policy can expose visibility lag?

<details><summary>Answer</summary>

Eventual consistency permits such a result.

</details>

4. Why check indexed_rows?

<details><summary>Answer</summary>

A finished status may coexist with rows still awaiting an index.

</details>

5. What does the BM25 function generate?

<details><summary>Answer</summary>

A sparse representation derived from analyzed text.

</details>

6. How can two correct reads differ?

<details><summary>Answer</summary>

They may be allowed to observe different applied revisions.

</details>

## Key takeaways

- A closed batch that can proceed through index construction.
- Routing into physical partitions, subject to the configured partition count.
- Eventual consistency permits such a result.
- A sparse representation derived from analyzed text.
- They may be allowed to observe different applied revisions.

## Clean up

Stop the service with `docker compose -f docker/compose.yaml --profile milvus down`. Named volumes retain data for the next session. Preview course-owned data with `uv run python scripts/cleanup.py` before using its removal option. 

## Go deeper

Compare the [primary documentation](https://milvus.io/docs/full-text-search.md) with the [recorded results](results/README.md). 

## Next: Module 16

Continue to [The wider database landscape](../16_landscape/README.md).
