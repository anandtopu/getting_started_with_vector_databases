"""Exercise smoke and acceptance checks for 12_pgvector."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_reference(exercise, tmp_path):
    check(
        "12_pgvector",
        exercise,
        load(ROOT / "modules/12_pgvector/solutions" / f"{exercise}.py").solve,
        tmp_path,
    )


@pytest.mark.parametrize("exercise", ["01_practice", "02_apply", "03_stretch"])
def test_starter(exercise):
    smoke(load(ROOT / "modules/12_pgvector/exercises" / f"{exercise}.py"))
