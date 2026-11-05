"""Reference acceptance; the same verify function accepts a learner project module."""

from pathlib import Path

from common.exercise_checks import load


def verify(project, tmp_path):
    result = project.evaluate("tinyvec")
    assert set(result) >= {"search", "rag", "recommendations_and_duplicates", "photo", "restore"}
    assert result["restore"]["resurrected_deletions"] == 0
    assert result["restore"]["lost_acknowledged_writes"] == 5
    assert result["rag"]["exact_passage_recall4"] >= 0.9


def test_capstone_05(tmp_path):
    root = Path(__file__).resolve().parents[1]
    load(root / "starter/project.py").main()
    verify(load(root / "solution/project.py"), tmp_path)
