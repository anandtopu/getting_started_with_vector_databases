"""Run each available course example/use case with the current interpreter.

Run: uv run python scripts/run_all_examples.py
Examples marked '# course-profile: name' are skipped unless --docker is supplied.
Each file gets a timeout. A skipped file is reported, never counted as passed.
"""

import argparse
import importlib.util
import os
import subprocess
import sys

from common.lesson_runtime import PACKAGES, requirements
from common.settings import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docker", action="store_true")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--module", help="Run only a module directory name, such as 00_setup")
    args = parser.parse_args()
    files = sorted(
        {
            *ROOT.glob("examples/*.py"),
            *ROOT.glob("modules/**/examples/*.py"),
            *ROOT.glob("modules/**/use_case/*.py"),
        }
    )
    if args.module:
        files = [path for path in files if args.module in path.parts]
    if not files:
        raise SystemExit("No examples found")
    failures = []
    skipped = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        extras, profile = requirements(source)
        missing = [extra for extra in extras if importlib.util.find_spec(PACKAGES[extra]) is None]
        if missing:
            print(f"SKIP {path.relative_to(ROOT)}: install extras {missing}")
            skipped.append(path)
            continue
        if profile and not args.docker:
            print(f"SKIP Docker example: {path.relative_to(ROOT)}")
            skipped.append(path)
            continue
        print(f"RUN {path.relative_to(ROOT)}", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                cwd=ROOT,
                timeout=args.timeout,
                env={**os.environ, "PYTHONUTF8": "1"},
            )
            if result.returncode:
                failures.append(str(path.relative_to(ROOT)))
        except subprocess.TimeoutExpired:
            failures.append(f"{path.relative_to(ROOT)} (timeout)")
    print(
        f"{len(files) - len(skipped) - len(failures)} passed; {len(skipped)} skipped; {len(failures)} failed."
    )
    if failures:
        raise SystemExit("Failed: " + ", ".join(failures))


if __name__ == "__main__":
    main()
