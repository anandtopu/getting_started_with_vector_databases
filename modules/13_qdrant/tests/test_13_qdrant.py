"""Exercise smoke and acceptance checks for 13_qdrant."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_reference(exercise, tmp_path):
    check(
        "13_qdrant",
        exercise,
        load(ROOT / "modules/13_qdrant/solutions" / f"{exercise}.py").solve,
        tmp_path,
    )


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_starter(exercise):
    smoke(load(ROOT / "modules/13_qdrant/exercises" / f"{exercise}.py"))
