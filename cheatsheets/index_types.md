# Index types | At a glance

## Exact flat

Visits all eligible vectors. No ANN recall loss, but work grows with corpus size and dimension. Excellent correctness reference and often sufficient for small filtered sets.

## LSH

Randomized hash buckets make similar points likely candidates. More tables/probes improve coverage at memory/query cost; sparse candidate sets can hurt recall.

## IVF

Train coarse centroids, assign vectors to lists, and probe nearby lists. nprobe trades query work for recall. Training mismatch and uneven lists can dominate performance.

## HNSW

Search a hierarchy of proximity graphs. M affects graph size, efConstruction affects build effort, efSearch affects query exploration. Deletions and selective filters need explicit behavior.

## SQ / binary / PQ

SQ reduces coordinate precision; binary stores threshold/projection bits; PQ stores subvector codebook IDs. Rescoring can restore quality but retains full vectors and adds work. Include codebook overhead.

## Disk graph / RaBitQ

Disk indexes trade RAM for I/O and depend on cache warmth. RaBitQ uses randomized quantization with a corrected estimator; the teaching version unpacks codes densely and makes no optimized-kernel claim.

## Selection rule

Begin with exact truth. Set a recall floor and resource budget, sweep on development data, test held-out queries once. Compare only matched workloads. See docs/INDEX_TUNING_GUIDE.md and results/leaderboard.md.
