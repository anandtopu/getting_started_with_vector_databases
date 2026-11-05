"""Reference acceptance and runnable-starter checks for module 03_tinyvec."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_reference_03_tinyvec(name, tmp_path):
    path = ROOT / "modules/03_tinyvec/solutions" / f"{name}.py"
    check("03_tinyvec", name, load(path).solve, tmp_path)


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_starter_03_tinyvec(name, tmp_path):
    path = ROOT / "modules/03_tinyvec/exercises" / f"{name}.py"
    smoke(load(path))
