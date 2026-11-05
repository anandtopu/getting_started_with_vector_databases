"""Reference acceptance and runnable-starter checks for module 02_embeddings."""

import pytest

from common.exercise_checks import check, load, smoke
from common.settings import ROOT


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_reference_02_embeddings(name, tmp_path):
    path = ROOT / "modules/02_embeddings/solutions" / f"{name}.py"
    check("02_embeddings", name, load(path).solve, tmp_path)


@pytest.mark.parametrize("name", ["01_practice", "02_apply", "03_stretch"])
def test_starter_02_embeddings(name, tmp_path):
    path = ROOT / "modules/02_embeddings/exercises" / f"{name}.py"
    smoke(load(path))
