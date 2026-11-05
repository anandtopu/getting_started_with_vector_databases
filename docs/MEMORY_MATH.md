# Memory math: payload, capacity and measured usage

For N records with d dimensions and b bytes per number, raw vector bytes are **N × d × b**. Decimal GB divide by 10^9; GiB divide by 2^30. Neither number is process resident memory.

| Representation for 10M × 768 | Payload bytes | GB | GiB |
|---|---:|---:|---:|
| float32 | 30,720,000,000 | 30.72 | 28.61 |
| float16 | 15,360,000,000 | 15.36 | 14.31 |
| int8 | 7,680,000,000 | 7.68 | 7.15 |
| PQ: 96 one-byte codes per row | 960,000,000 | 0.96 | 0.89 |

The PQ example uses 96 subquantizers, each encoding eight dimensions with 256 centroids. A single shared float32 codebook adds 96 × 256 × 8 × 4 = 786,432 bytes. Coarse centroids, IDs, offsets and index structures add more. If you retain float32 vectors for exact rescoring, add their entire 30.72 GB back. Quantization changes accuracy; evaluate recall and ranking quality. float16 or int8 input can be expanded internally by a backend, so verify actual storage rather than inferring it from a Python dtype.

## A transparent planning estimate

`common/ops/capacity.py` estimates graph bytes as N × links × 8. With 32 links this is 2.56 GB. This is a simplified neighbor-ID budget, not an exact HNSW layout: upper levels, headers, allocation and the native base-layer layout differ by implementation. Metadata at an assumed 256 bytes per item adds another 2.56 GB. IDs, payload indexes, token indexes, WAL, sparse vectors, runtime buffers and model weights need separate budgets.

For float32 vectors, those three terms total **35.84 GB** per full copy. Two replicas total **71.68 GB**. Reserving 30% of provisioned capacity as spare space means dividing by 0.70, giving **102.4 GB / 95.37 GiB**. Multiplying by 1.30 would reserve less than 30% of the resulting capacity. Sharding divides per-node data; it does not reduce total logical payload. Replication increases total copies. Tenant skew can make the busiest shard the real constraint.

```text
uv run python scripts/memory_calculator.py --rows 10000000 --dimensions 768 --replicas 2 --width 4
```

The calculator labels its exclusions. Plan separate space for blue and green collections during model migration, temporary compaction files and an independently stored backup. A green 1024-dimensional float32 model has a different payload from a blue 384-dimensional one. A model migration can temporarily require both encoders in memory too.

## Measure fit before purchasing capacity

1. Establish a fresh-process baseline RSS, load models separately and record process peak RSS.
2. Build a representative index and measure both process and server memory, plus persisted bytes after the intended maintenance operation.
3. Run the intended filters, update/delete churn, batch ingestion and concurrent searches.
4. Measure the worst temporary build/compaction/migration peak, not just steady state.
5. Test a node loss with the expected remaining capacity. Keep headroom for rebalancing.

The [Tier 5 evidence](../results/tier5/README.md) measures local SQLite reclamation, a 2,000-vector tuning experiment, API load and a small three-peer failure drill. It does **not** load ten million vectors or establish that this laptop can serve the planned capacity. Existing [Tier 2 results](../docs/PHASE_4_REPORT.md) distinguish process memory from index payload. Native server memory is unmeasured in the Tier 5 checkpoint; no zero is substituted for a missing measurement.

## Cost worksheet

Use the same workload, durability, replica count and operator coverage on both sides. `monthly_cost` returns separate compute (730 hours × hourly price), storage, request, egress and operator-labor terms. Example inputs of $0.50/hour, 100 GiB at $0.10/GiB-month and eight operator hours at $75 yield $975/month. Example managed inputs of $1.20/hour, 100 GiB at $0.20 and two operator hours at $75 yield $1,046/month. These are **hypothetical USD teaching inputs dated November 2026**, not provider quotes or a buying recommendation. Discounts, backups, availability zones, minimum service units, taxes and support can change the result.

For an immutable local catalog, exact NumPy/FAISS may be enough. Embedded storage adds local durability and convenient queries. A server becomes useful when shared mutation, independent scaling, operational isolation or access control justify its costs. Start from requirements rather than a row-count threshold.
