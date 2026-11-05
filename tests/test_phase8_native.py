"""Explicit TLS-server regression: shared secure routes use the real chosen database."""

import pytest


@pytest.mark.docker
@pytest.mark.allow_hosts(["127.0.0.1", "localhost", "::1"])
def test_secure_qdrant_routes_and_restart(tmp_path):
    pytest.importorskip("qdrant_client")
    pytest.importorskip("fastapi")
    from common.exercise_checks import load
    from common.settings import ROOT

    checks = load(ROOT / "tests/test_tier5.py")
    checks.test_secure_all_routes_and_restart(tmp_path, "qdrant-secure")
