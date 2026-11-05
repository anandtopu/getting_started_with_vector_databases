"""Evaluate text-to-image, photo-to-image and weighted fusion.

Run: uv run  python modules/20_multimodal/examples/03_measure.py
Expected: held-out nDCG for each mode with self-image excluded.
CPU: seconds to one minute. Needs: base, frozen image/text artifacts. No implicit downloads.
"""

from common.apps.database import AppDatabase
from common.apps.evaluation import photo_evaluation
from common.teaching import evidence


def main() -> None:
    with AppDatabase() as db:
        # KEY IDEA: remove the query image ID before measuring relevance.
        result = photo_evaluation(db)
    print(result["held_out"])
    print(result["scope"])
    evidence("photo-search", result, tier=4)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
