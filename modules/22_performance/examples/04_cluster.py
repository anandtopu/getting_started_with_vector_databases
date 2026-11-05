"""Run the explicitly requested native qdrant-cluster experiment.
Run: uv run --extra qdrant python modules/22_performance/examples/04_cluster.py
CPU: about two minutes. Requires the Tier 5 runtime preparation and local setup.
Owns and cleans only the processes or UUID pods created by this invocation.
"""
# course-extra: qdrant
# course-profile: qdrant-cluster

from scripts.cluster_tier5 import main as run


def main():
    run()


if __name__ == "__main__":
    main()
