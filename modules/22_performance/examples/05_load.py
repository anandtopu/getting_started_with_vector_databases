"""Run the explicitly requested native api-load experiment.
Run: uv run --extra apps python modules/22_performance/examples/05_load.py
CPU: about two minutes. Requires the Tier 5 runtime preparation and local setup.
Owns and cleans only the processes or UUID pods created by this invocation.
"""
# course-extra: apps
# course-profile: api-load

from scripts.load_tier5 import main as run


def main():
    run()


if __name__ == "__main__":
    main()
