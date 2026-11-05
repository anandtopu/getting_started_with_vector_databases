"""Execute delivered lesson notebooks with a temporary kernel spec for this Python environment.

Run: uv run --extra notebooks --extra libs --extra embedded python scripts/run_notebooks.py
Writes executed copies under the course cache; source notebooks remain cleared.
Local kernel sockets are needed, but no external network, models, or Docker.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from common.errors import CourseError, run_cli
from common.io import atomic_json
from common.settings import ROOT, cache_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", help="Execute a single module directory name")
    selected = parser.parse_args().module
    try:
        import nbformat
        from jupyter_client.kernelspec import KernelSpecManager
        from nbclient import NotebookClient
    except ImportError as exc:
        raise CourseError("Install notebook tools: uv sync --extra notebooks") from exc
    os.environ["HF_HUB_OFFLINE"] = "1"
    destination = cache_dir() / "tier1" / "executed-notebooks"
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        kernel_root = Path(temporary)
        atomic_json(
            kernel_root / "course-python" / "kernel.json",
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "Course Python",
                "language": "python",
            },
        )
        manager = KernelSpecManager(kernel_dirs=[str(kernel_root)])
        paths = [
            *sorted((ROOT / "modules").glob("[0-9][0-9]_*/notebook.ipynb")),
            *sorted((ROOT / "modules/bonus").glob("B[1-4]_*/notebook.ipynb")),
        ]
        for path in paths:
            if selected and path.parent.name != selected:
                continue
            destination = (
                cache_dir()
                / (
                    "bonus"
                    if path.parent.name.startswith("B")
                    else "tier1"
                    if int(path.parent.name[:2]) < 5
                    else "tier2"
                    if int(path.parent.name[:2]) < 11
                    else "tier3"
                    if int(path.parent.name[:2]) < 17
                    else "tier4"
                    if int(path.parent.name[:2]) < 21
                    else "tier5"
                )
                / "executed-notebooks"
            )
            destination.mkdir(parents=True, exist_ok=True)
            notebook = nbformat.read(path, as_version=4)
            client = NotebookClient(
                notebook,
                timeout=300,
                kernel_name="course-python",
                resources={"metadata": {"path": str(ROOT)}},
            )
            client.create_kernel_manager()
            client.km.kernel_spec_manager = manager
            client.execute()
            nbformat.write(notebook, destination / f"{path.parent.name}.ipynb")
            print(
                f"PASS {path.parent.name}: {sum(c.cell_type == 'code' for c in notebook.cells)} code cells",
                flush=True,
            )


if __name__ == "__main__":
    run_cli(main)
