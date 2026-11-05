"""Exercise smoke and acceptance checks for 14_weaviate."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_reference(exercise, tmp_path):
    check(
        "14_weaviate",
        exercise,
        load(ROOT / "modules/14_weaviate/solutions" / f"{exercise}.py").solve,
        tmp_path,
    )


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_starter(exercise):
    smoke(load(ROOT / "modules/14_weaviate/exercises" / f"{exercise}.py"))
