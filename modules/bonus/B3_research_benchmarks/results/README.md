# Measured evidence

FAISS HNSW selected efSearch=10 on 60 development queries and scored 0.970 recall@10 on 60 held-out queries over 3,000 pixel vectors. Three repeats yielded 180 held-out timings; these are not 180 independent queries. [Raw](../../../../results/bonus/public-benchmark-50dee323.json).

Run `python scripts/verify_bonus.py --native --module B3_research_benchmarks` after the README setup. [Feature diagnostics](../../../../results/leaderboard.md#research_reproduction) and [execution records](../../../../results/bonus/README.md) preserve actual commands and environment. [Phase 8](../../../../docs/PHASE_8_REPORT.md) explains limits.
