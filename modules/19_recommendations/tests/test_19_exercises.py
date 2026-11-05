"""Reference solutions meet the same acceptance criteria offered to learners."""

from pathlib import Path

from common.exercise_checks import check, load, smoke


def test_starters_and_solutions(tmp_path):
    module = Path(__file__).resolve().parents[1]
    for starter in sorted((module / "exercises").glob("*.py")):
        smoke(load(starter))
        solution = module / "solutions" / starter.name
        check(module.name, starter.stem, load(solution).solve, tmp_path)
