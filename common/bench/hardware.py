"""Attach hardware, installed versions, lock hash, and source identity to every run."""

import importlib.metadata
import platform
import subprocess

import psutil

from common.io import digest, file_hash
from common.settings import ROOT


def hardware() -> dict:
    return {
        "os": platform.platform(),
        "machine": platform.machine(),
        "cpu": platform.processor() or "not reported",
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(),
        "ram_bytes": psutil.virtual_memory().total,
        "python": platform.python_version(),
    }


def provenance() -> dict:
    packages = {
        dist.metadata["Name"]: dist.version
        for dist in importlib.metadata.distributions()
        if dist.metadata.get("Name")
    }
    files = sorted(
        {
            *ROOT.glob("common/**/*.py"),
            *ROOT.glob("tinyvec/**/*.py"),
            *ROOT.glob("scripts/*.py"),
            *ROOT.glob("modules/**/*.py"),
            *ROOT.glob("capstones/**/*.py"),
            *ROOT.glob("modules/bonus/*/src/*.ts"),
            *ROOT.glob("modules/bonus/*/package*.json"),
            *ROOT.glob("playground/**/*.py"),
            ROOT / "pyproject.toml",
        }
    )
    hashes = {
        str(p.relative_to(ROOT)).replace("\\", "/"): file_hash(p)
        for p in files
        if p.is_file() and not {"node_modules", "dist", "__pycache__"}.intersection(p.parts)
    }
    commit = None
    dirty = None
    try:
        output = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=5
        )
        if output.returncode == 0:
            commit = output.stdout.strip()
            dirty = bool(
                subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=5,
                ).stdout.strip()
            )
    except (OSError, subprocess.TimeoutExpired):
        commit = None
    return {
        "packages": dict(sorted(packages.items())),
        "git_commit": commit,
        "git_dirty": dirty,
        "source_hash": digest(hashes),
        "source_files": hashes,
        "uv_lock_sha256": file_hash(ROOT / "uv.lock") if (ROOT / "uv.lock").exists() else None,
    }
