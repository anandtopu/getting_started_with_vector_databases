"""Smoke starters and independently accept reference solutions."""

from pathlib import Path

from common.exercise_checks import check, load, smoke


def test_bonus_b1(tmp_path):
    module = Path(__file__).resolve().parents[1]
    for starter in (module / "exercises").glob("*.py"):
        smoke(load(starter))
        check(module.name, starter.stem, load(module / "solutions" / starter.name).solve, tmp_path)
