"""Reference acceptance; the same verify function accepts a learner project module."""

from pathlib import Path

from common.exercise_checks import load


def verify(project, tmp_path):
    result = project.scenario(tmp_path)
    assert result["isolation"] and result["restart_deletion"]
    assert result["deleted"]["purged_snapshots"]


def test_capstone_04(tmp_path):
    root = Path(__file__).resolve().parents[1]
    load(root / "starter/project.py").main()
    verify(load(root / "solution/project.py"), tmp_path)
