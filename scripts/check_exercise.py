"""Check any selected starter or solution against the same acceptance criteria.

Run: uv run python scripts/check_exercise.py modules/01_vectors_similarity/exercises/01_practice.py
Add --smoke to check only that the starter runs. No network, models, or Docker.
"""

import argparse
import tempfile
from pathlib import Path

from common.exercise_checks import check, load, smoke


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("implementation", type=Path)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    selected = load(args.implementation)
    try:
        if args.smoke:
            smoke(selected)
        else:
            with tempfile.TemporaryDirectory() as directory:
                check(
                    args.implementation.parent.parent.name,
                    args.implementation.stem,
                    selected.solve,
                    Path(directory),
                )
    except (AssertionError, ValueError) as exc:
        raise SystemExit(
            f"Not yet: {exc}. Read this exercise's criteria in the module README."
        ) from exc
    print("Passed " + ("starter smoke check." if args.smoke else "acceptance checks."))


if __name__ == "__main__":
    main()
