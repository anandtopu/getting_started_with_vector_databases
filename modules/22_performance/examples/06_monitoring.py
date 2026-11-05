"""Run the explicitly requested native monitoring experiment.
Run: uv run --extra ops python modules/22_performance/examples/06_monitoring.py
CPU: about two minutes. Requires the Tier 5 runtime preparation and local setup.
Owns and cleans only the processes or UUID pods created by this invocation.
"""
# course-extra: ops
# course-profile: monitoring

from scripts.monitor_tier5 import main as run


def main():
    run()


if __name__ == "__main__":
    main()
