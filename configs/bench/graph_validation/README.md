# Fixed-budget graph validation

The throughput-selected graph reached 0.896 on the original held-out hashing fixture, just below the 0.900 target. Keep that result. For an accuracy-oriented alternative, fix the larger budgets **before** measuring: M=12, efConstruction=64 and efSearch=96, with one original candidate per requested position before the graph's search beam applies. Report recall, query latency, build cost and link bytes even if the new setting misses.

Run the development configuration first, then the original test split as a regression check. Run the fresh-products configuration once with the preselected seed 20261105. This last run changes the seeded fixture products and query sampling; it reuses the synthetic intent templates. It tests transfer to another corpus draw. For each run use `uv run python scripts/run_bench.py configs/bench/graph_validation/NAME.yaml` and replace NAME with the configuration stem. Only compare timings within matching workload hashes.
