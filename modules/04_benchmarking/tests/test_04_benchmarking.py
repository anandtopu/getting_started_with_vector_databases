"""Reference acceptance and runnable-starter checks for module 04_benchmarking."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_reference_04_benchmarking(name, tmp_path):
    path = ROOT / "modules/04_benchmarking/solutions" / f"{name}.py"
    check("04_benchmarking", name, load(path).solve, tmp_path)


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_starter_04_benchmarking(name, tmp_path):
    path = ROOT / "modules/04_benchmarking/exercises" / f"{name}.py"
    smoke(load(path))
