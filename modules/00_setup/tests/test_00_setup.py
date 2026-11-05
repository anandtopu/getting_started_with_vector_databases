"""Reference acceptance and runnable-starter checks for module 00_setup."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_reference_00_setup(name, tmp_path):
    path = ROOT / "modules/00_setup/solutions" / f"{name}.py"
    check("00_setup", name, load(path).solve, tmp_path)


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_starter_00_setup(name, tmp_path):
    path = ROOT / "modules/00_setup/exercises" / f"{name}.py"
    smoke(load(path))
