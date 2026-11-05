"""Run the same acceptance contract against a selected learner or reference project.
Run: uv run python scripts/check_capstone.py capstones/01_tinyvec/solution/project.py
Expected: acceptance passed, or an actionable incomplete-contract message. CPU: seconds.
Add --smoke for a runnable starter. No implicit model downloads or services.
"""

import argparse
import sys
import tempfile
from pathlib import Path

from common.exercise_checks import load


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("implementation", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    root = args.implementation.resolve().parents[1]
    checks = list((root / "tests").glob("test_*_project.py"))
    if len(checks) != 1:
        parser.error("Select a project.py inside a capstone starter or solution directory")
    project = load(args.implementation)
    try:
        if args.smoke:
            sys.argv = [str(args.implementation)]
            project.main()
        else:
            with tempfile.TemporaryDirectory() as temporary:
                load(checks[0]).verify(project, Path(temporary))
    except (AssertionError, AttributeError, ValueError) as exc:
        raise SystemExit(f"Not yet: {exc}. Read this capstone's acceptance criteria.") from exc
    print("Passed starter smoke." if args.smoke else "Passed capstone acceptance.")


if __name__ == "__main__":
    main()
