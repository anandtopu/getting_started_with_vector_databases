"""Reference acceptance; the same verify function accepts a learner project module."""

from pathlib import Path

import pytest

from common.exercise_checks import load


def verify(project, tmp_path):
    assistant = project.HelpProject("tinyvec")
    try:
        result = assistant.ask("rag-000")
        assert result["mode"] == "source_excerpt"
        assert result["citations"] and result["citations"][0] in result["answer"]
        assert result["answer"].split(" [")[0] in result["evidence"]
        with pytest.raises(ValueError):
            assistant.ask("missing")
    finally:
        assistant.close()


def test_capstone_03(tmp_path):
    root = Path(__file__).resolve().parents[1]
    load(root / "starter/project.py").main()
    verify(load(root / "solution/project.py"), tmp_path)
