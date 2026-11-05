"""Reference acceptance; the same verify function accepts a learner project module."""

from pathlib import Path

from common.exercise_checks import load


def verify(project, tmp_path):
    def row(name, recall, latency, errors=0):
        return {
            "config": {"backend": name},
            "run_id": name,
            "summary": {"recall_at_k": recall, "p95_ms": latency, "errors": errors},
        }

    assert project.recommend([row("fast-bad", 0.5, 1), row("valid", 1, 5)])["choice"] == "valid"
    assert project.recommend([row("broken", 1, 1, 1)])["choice"] is None
    assert project.recommend([])["choice"] is None


def test_capstone_02(tmp_path):
    root = Path(__file__).resolve().parents[1]
    load(root / "starter/project.py").main()
    verify(load(root / "solution/project.py"), tmp_path)
