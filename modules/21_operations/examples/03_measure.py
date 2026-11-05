"""Measure native page reclamation and fresh-process disaster recovery.
Run: uv run python modules/21_operations/examples/03_measure.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""

from common.ops.drills import disaster_recovery, operations, sqlite_compaction


def main():
    print(operations())
    print(sqlite_compaction())
    recovered = disaster_recovery()
    assert recovered["lost_acknowledged_writes"] == 5
    assert recovered["resurrected_deletions"] == 0
    print(recovered)


if __name__ == "__main__":
    main()
