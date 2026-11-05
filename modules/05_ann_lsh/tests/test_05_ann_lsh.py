"""Check the exercise contracts and confirm the provided starters are runnable."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_solution(exercise, tmp_path):
    path = ROOT / "modules/05_ann_lsh/solutions" / f"{exercise}.py"
    check("05_ann_lsh", exercise, load(path).solve, tmp_path)


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_starter(exercise):
    smoke(load(ROOT / "modules/05_ann_lsh/exercises" / f"{exercise}.py"))
