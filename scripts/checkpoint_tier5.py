"""Run operations, recovery and tuning drills with append-only provenance.
Run: uv run python scripts/checkpoint_tier5.py
CPU: under a minute; --native additionally requires the secure Qdrant profile.
"""

import argparse
import uuid
from datetime import UTC, datetime

from common.bench.hardware import hardware, provenance
from common.io import atomic_json, file_hash
from common.ops.capacity import estimate, monthly_cost
from common.ops.drills import (
    cache_measurement,
    disaster_recovery,
    operations,
    sqlite_compaction,
    target_tuning,
)
from common.settings import ROOT, data_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true")
    args = parser.parse_args()
    results = {}
    for run in [operations, sqlite_compaction, disaster_recovery, cache_measurement, target_tuning]:
        print("Running", run.__name__, flush=True)
        results[run.__name__] = run()
    results["capacity"] = estimate(replicas=2)
    results["hypothetical_cost"] = {
        "self_hosted": monthly_cost(
            hourly_compute=0.5,
            storage_gib=100,
            storage_rate=0.1,
            operator_hours=8,
            operator_rate=75,
        ),
        "managed": monthly_cost(
            hourly_compute=1.2,
            storage_gib=100,
            storage_rate=0.2,
            operator_hours=2,
            operator_rate=75,
        ),
        "scope": "Illustrative USD assumptions, not vendor quotes; 730 hours/month",
    }
    if args.native:
        from common.ops.native import native_migration_restore, native_security

        results["native_security"] = native_security()
        results["native_migration_restore"] = native_migration_restore()
    path = ROOT / "results/tier5" / f"checkpoint-{uuid.uuid4().hex[:8]}.json"
    atomic_json(
        path,
        {
            "created_at": datetime.now(UTC).isoformat(),
            "hardware": hardware(),
            "provenance": provenance(),
            "command": "python scripts/checkpoint_tier5.py" + (" --native" if args.native else ""),
            "artifact_sha256": file_hash(data_dir() / "embeddings_10k.parquet"),
            "observations": results,
        },
    )
    print(path)


if __name__ == "__main__":
    main()
