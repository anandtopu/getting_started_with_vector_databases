"""Export the tested lock for a pip/venv fallback; does not guess transitive versions.

Run: uv run python scripts/export_requirements.py --output requirements.txt
Add --extra embedded or another extra as needed. Requires uv; no Docker or model.
"""

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("requirements.txt"))
    parser.add_argument("--extra", action="append", default=[])
    args = parser.parse_args()
    command = [
        "uv",
        "export",
        "--frozen",
        "--format",
        "requirements-txt",
        "--no-emit-project",
        "--output-file",
        str(args.output),
    ]
    for extra in args.extra:
        command += ["--extra", extra]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
