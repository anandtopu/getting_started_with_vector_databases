"""Reference acceptance and runnable-starter checks for module 01_vectors_similarity."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_reference_01_vectors_similarity(name, tmp_path):
    path = ROOT / "modules/01_vectors_similarity/solutions" / f"{name}.py"
    check("01_vectors_similarity", name, load(path).solve, tmp_path)


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_starter_01_vectors_similarity(name, tmp_path):
    path = ROOT / "modules/01_vectors_similarity/exercises" / f"{name}.py"
    smoke(load(path))
