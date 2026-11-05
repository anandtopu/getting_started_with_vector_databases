"""Enumerate only course-owned generated resources; reject links and escaped paths."""

import shutil
import subprocess
from pathlib import Path

from common.errors import CourseError

GENERATED = (
    ".cache/marlowe",
    "data/generated",
    "data/images",
    "data/benchmarks",
    "data/products.parquet",
    "data/reviews.parquet",
    "data/events.parquet",
    "data/duplicates.parquet",
    "data/generated-manifest.json",
    "data/embeddings_full.parquet",
    "data/embeddings_full.manifest.json",
)
PROJECT = "marlowe-vector-course"


def safe_target(root: Path, relative: str) -> Path:
    root = root.resolve()
    path = root / relative
    if path.is_symlink() or path.is_junction() or root not in path.resolve().parents:
        raise CourseError(f"Refusing cleanup outside course directory or through a link: {path}")
    for parent in path.parents:
        if parent == root:
            break
        if parent.is_symlink() or parent.is_junction():
            raise CourseError(f"Refusing linked cleanup parent: {parent}")
    return path


def local_resources(root: Path) -> list[dict]:
    resources = []
    for relative in GENERATED:
        path = safe_target(root, relative)
        if path.exists():
            if path.is_dir():
                children = list(path.rglob("*"))
                if any(p.is_symlink() or p.is_junction() for p in children):
                    raise CourseError(f"Refusing a directory containing links: {path}")
                size = sum(p.stat().st_size for p in children if p.is_file())
            else:
                size = path.stat().st_size
            resources.append({"path": relative, "bytes": size})
    return resources


def docker_resources(project=PROJECT) -> dict:
    if project not in {PROJECT, "marlowe-tier5"}:
        raise CourseError("Unrecognized course Compose project")
    if not shutil.which("docker"):
        return {"available": False, "reason": "Docker CLI not installed"}
    result = {}
    for resource, command in {
        "containers": [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"label=com.docker.compose.project={project}",
            "--format",
            "{{.Names}}",
        ],
        "volumes": [
            "docker",
            "volume",
            "ls",
            "--filter",
            f"label=com.docker.compose.project={project}",
            "--format",
            "{{.Name}}",
        ],
        "networks": [
            "docker",
            "network",
            "ls",
            "--filter",
            f"label=com.docker.compose.project={project}",
            "--format",
            "{{.Name}}",
        ],
    }.items():
        try:
            response = subprocess.run(command, capture_output=True, text=True, timeout=8)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"available": False, "reason": str(exc)}
        if response.returncode:
            return {"available": False, "reason": response.stderr.strip()}
        result[resource] = response.stdout.splitlines()
    return {"available": True, **result}


def remove_local(root: Path, resources: list[dict]) -> None:
    for resource in resources:
        if resource["path"] not in GENERATED:
            raise CourseError("Unrecognized cleanup target")
        path = safe_target(root, resource["path"])
        if path.is_dir():
            if any(p.is_symlink() or p.is_junction() for p in path.rglob("*")):
                raise CourseError("Cleanup target changed to contain a link; refusing removal")
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
