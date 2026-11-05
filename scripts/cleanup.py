"""Preview generated course resources; --remove asks before deleting them.

Run: uv run python scripts/cleanup.py
Then: uv run python scripts/cleanup.py --remove
Preserves committed fixtures/vectors, source, .venv, shared model caches, and Docker images.
No global prune. Only the two explicitly named course Compose projects are eligible.
"""

import argparse
import json
import subprocess

from common.cleanup import PROJECT, docker_resources, local_resources, remove_local
from common.errors import CourseError, run_cli
from common.settings import ROOT, cache_dir, data_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()
    if data_dir() != ROOT / "data" or cache_dir() != ROOT / ".cache/marlowe":
        raise CourseError(
            "Custom data/cache locations are configured. Restore the default paths before using course cleanup; external paths are never deleted."
        )
    local = local_resources(ROOT)
    docker = docker_resources()
    advanced = docker_resources("marlowe-tier5")
    print(json.dumps({"local": local, "docker": docker, "tier5_docker": advanced}, indent=2))
    if not args.remove:
        print("Preview only. Use --remove to review this list and confirm deletion.")
        return
    if input("Delete exactly these generated course resources? Type DELETE: ") != "DELETE":
        print("Cancelled; nothing removed.")
        return
    if docker["available"] and any(docker[key] for key in ("containers", "volumes", "networks")):
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(ROOT / "docker/compose.yaml"),
                "-p",
                PROJECT,
                "--profile",
                "*",
                "down",
                "--volumes",
                "--remove-orphans",
            ],
            check=True,
        )
    if advanced["available"] and any(
        advanced[key] for key in ("containers", "volumes", "networks")
    ):
        subprocess.run(
            [
                "docker",
                "compose",
                "--env-file",
                str(cache_dir() / "tier5/runtime/compose.env"),
                "-f",
                str(ROOT / "docker/compose.tier5.yaml"),
                "-p",
                "marlowe-tier5",
                "down",
                "--volumes",
                "--remove-orphans",
            ],
            check=True,
        )
    remove_local(ROOT, local)
    print(
        "Removed the listed local resources. Docker was unavailable and not changed."
        if not docker["available"]
        else "Removed the listed course resources."
    )


if __name__ == "__main__":
    run_cli(main)
