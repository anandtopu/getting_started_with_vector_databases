"""Runnable starting point for Capstone 02.
Run: uv run python capstones/02_database_bakeoff/starter/project.py
Expected: a working baseline, not completed acceptance. CPU: seconds.
Needs: included vectors; no downloads, credentials or containers.
"""

from common.bench.config import BenchConfig


def plan():
    # YOUR CODE HERE: add three matched databases and evaluate an explicit recall gate.
    return [BenchConfig(name="starter-exact", backend="tinyvec", limit=100, queries=10)]


def main() -> None:
    print([c.model_dump() for c in plan()])


if __name__ == "__main__":
    main()
