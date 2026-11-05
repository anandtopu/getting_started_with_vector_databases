"""Use a native clustering library to tune recall on development queries only.
Run: uv run python modules/22_performance/examples/02_production.py
CPU: seconds to a minute; 2 GB RAM for frozen fixtures. No model downloads.
Read the module's setup for optional extras and server requirements.
"""

from common.ops.drills import target_tuning


def main():
    result = target_tuning()
    print(result)
    assert result["chosen_nprobe"] is not None
    assert result["heldout"]["samples"] == 30
    print("A held-out miss must be reported; never retune on the test split.")


if __name__ == "__main__":
    main()
