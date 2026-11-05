"""Exercise smoke and acceptance checks for 11_embedded."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_reference(exercise, tmp_path):
    check(
        "11_embedded",
        exercise,
        load(ROOT / "modules/11_embedded/solutions" / f"{exercise}.py").solve,
        tmp_path,
    )


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_starter(exercise):
    smoke(load(ROOT / "modules/11_embedded/exercises" / f"{exercise}.py"))
