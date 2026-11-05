"""Verify included source/vector artifacts or explicitly refresh their inventory.

Run: uv run python scripts/verify_artifacts.py
After intentional regeneration: add --refresh. No network or model required.
This checks bytes; artifact tests separately check ID/content/model alignment.
"""

import argparse
import json

from common.errors import CourseError, run_cli
from common.io import atomic_json, file_hash
from common.settings import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    directory = ROOT / "data"
    manifest = directory / "manifest.json"
    if args.refresh:
        paths = [
            directory / name
            for name in (
                "products_10k.parquet",
                "embeddings_10k.parquet",
                "embeddings_10k.manifest.json",
                "query_embeddings.parquet",
                "query_embeddings.manifest.json",
                "sellers.json",
            )
        ]
        for name in ("eval", "help_center", "fixtures", "tier2", "tier4"):
            paths.extend(path for path in (directory / name).rglob("*") if path.is_file())
        atomic_json(
            manifest,
            {
                "format": 1,
                "seed": 20261104,
                "license": "MIT synthetic data; pinned pretrained model identities in the embedding and tier2 manifests; weights not included",
                "files": {
                    path.relative_to(directory).as_posix(): {
                        "bytes": path.stat().st_size,
                        "sha256": file_hash(path),
                    }
                    for path in sorted(paths)
                },
            },
        )
    inventory = json.loads(manifest.read_text(encoding="utf-8"))
    for name, entry in inventory["files"].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()) or not path.is_file():
            raise CourseError(f"Missing or unsafe artifact path: {name}")
        if path.stat().st_size != entry["bytes"] or file_hash(path) != entry["sha256"]:
            raise CourseError(
                f"Artifact checksum failed: {name}. Restore or regenerate matching data."
            )
    print(f"Verified {len(inventory['files'])} included artifacts.")


if __name__ == "__main__":
    run_cli(main)
