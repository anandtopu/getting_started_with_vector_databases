"""Explicit setup boundaries for optional Node and native bonus experiments."""

import json
import os
import shutil
import subprocess
from pathlib import Path

from common.errors import CourseError
from common.settings import ROOT, cache_dir


def typescript(backend):
    folder = ROOT / "modules/bonus/B1_other_languages"
    if backend not in {"qdrant", "weaviate"}:
        raise ValueError("Choose a documented TypeScript backend")
    fixture = Path(os.environ.get("MARLOWE_TS_FIXTURE", str(cache_dir() / "bonus/ts-fixture.json")))
    node = shutil.which("node")
    if node is None or not (folder / "dist/native.js").exists() or not fixture.exists():
        raise CourseError(
            "Install Node 22+, then cd modules/bonus/B1_other_languages; npm ci; npm run build. Export vectors with python scripts/prepare_bonus.py."
        )
    result = subprocess.run(
        [node, "dist/native.js", backend],
        cwd=folder,
        capture_output=True,
        text=True,
        encoding="utf8",
        timeout=90,
        env={**os.environ, "MARLOWE_TS_FIXTURE": str(fixture.resolve())},
    )
    if result.returncode:
        raise CourseError(result.stderr[-1500:])
    return json.loads(result.stdout.strip().splitlines()[-1])


def typescript_check():
    folder = ROOT / "modules/bonus/B1_other_languages"
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if npm is None or not (folder / "node_modules/typescript").exists():
        raise CourseError("Install Node 22+ and run npm ci in modules/bonus/B1_other_languages")
    for args in [["run", "build"], ["test"]]:
        result = subprocess.run(
            [npm, *args], cwd=folder, capture_output=True, text=True, encoding="utf8", timeout=90
        )
        if result.returncode:
            raise CourseError(result.stdout + result.stderr)
    return {
        "build": "passed",
        "node_contract_tests": "passed",
        "node_version": subprocess.check_output(
            [shutil.which("node"), "--version"], text=True
        ).strip(),
    }
