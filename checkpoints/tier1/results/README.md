# Tier 1 reference submission

The checkpoint ran a saved semantic query over 1,000 products, saved TinyVec, and launched a fresh Python process that loaded the snapshot and returned the same five IDs. This checks an actual restore, not just serialization in the original process.

**Playground session:** the Streamlit interaction runner opened the default TinyVec catalog, searched q000 at k=5, then submitted maximum price $30 and region north. The original results included `p0000280` at $30.33 in west; that item disappears when eligibility changes. `p0000980` at $24.89 in north enters the top five. All filtered results satisfy both constraints. The [recorded session](submission.json) contains the complete before/after tables. This is an executed interaction, not a visual browser inspection.

**Benchmark:** cosine, 384-dimensional float16-rounded MiniLM vectors, k=10, 20 warm-ups and 100 queries × five repetitions. Neighbor recall was 1.000; synthetic precision was 0.654, MRR 0.680, and nDCG 0.840. Perfect exact-neighbor recall did not make every neighbor a useful answer. Request p50/p95/p99 were 0.635/1.571/2.638 ms. Serial throughput was 1188.0 ± 140.5 QPS across repetitions. Snapshot size was 2,193,916 bytes. The [raw benchmark](benchmark-method-20261104T224314-f1bea343.json) records build, insertion, sampled RSS, hardware, configuration, and all requests.

**Decision:** the exact store is adequate as a correctness reference and a local experiment. These results do not establish service concurrency, durability under arbitrary failures, human relevance, or performance on another machine. More realistic judgments and a workload-specific latency budget are needed before changing architecture.
