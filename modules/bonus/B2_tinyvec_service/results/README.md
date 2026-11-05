# Measured evidence

Four callers acknowledged 20 mutations; restarting recovered sequence 20. Separate tests cover abrupt process exit, torn tail, complete-frame corruption and writer ownership. [Service raw](../../../../results/bonus/durable-service-05459c2a.json). Storage access is serialized and power loss is not simulated.

Run `python scripts/verify_bonus.py --native --module B2_tinyvec_service` after the README setup. [Feature diagnostics](../../../../results/leaderboard.md#tinyvec_service) and [execution records](../../../../results/bonus/README.md) preserve actual commands and environment. [Phase 8](../../../../docs/PHASE_8_REPORT.md) explains limits.
