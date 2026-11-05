"""Run starters separately from reference acceptance checks."""

from pathlib import Path

from common.exercise_checks import check, load, smoke


def test_starters_and_solutions(tmp_path):
    module = Path(__file__).resolve().parents[1]
    for starter in sorted((module / "exercises").glob("*.py")):
        smoke(load(starter))
        check(module.name, starter.stem, load(module / "solutions" / starter.name).solve, tmp_path)
