# 09_disk_scale · measured results

Windows-11-10.0.26300-SP0, Python 3.12.13, Intel64 Family 6 Model 198 Stepping 2, GenuineIntel. The generated disk workload uses int8 codes and independent float ground truth. Storage fragment costs are modeled separately.

[Raw lesson observation](disk-scale-2feb9a11.json)

The generated workload contains 1,000,000 unit vectors of 32 dimensions. The int8 file occupied 32,000,128 bytes including its header. Five queries averaged 0.980 recall@10 against the uncompressed float reference. Median scan time was 88.1 ms. Peak process RSS was 125.4 MiB. File generation plus independent truth took 0.85 s. OS page cache state was uncontrolled.

In the separate [page-read trace](page-reads-8490995b.json), 40 real adjacency records produced recall 1.00. The object-fragment figures are modeled bytes for those reads. No cloud requests were made.

[Central leaderboard](../../../results/leaderboard.md) · [Tier 2 checkpoint analysis](../../../checkpoints/tier2/results/README.md).
