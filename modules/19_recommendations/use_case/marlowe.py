"""Use the integrated Marlowe application in a realistic customer flow.

Run: uv run  python modules/19_recommendations/use_case/marlowe.py
Expected: retrieved products or cited policy passages.
CPU: seconds to one minute. Needs: base, prepared Tier 4 artifacts. No implicit downloads.
"""

from common.apps.marlowe import MarloweSearch


def main() -> None:
    with MarloweSearch() as app:
        # KEY IDEA: duplicate detection proposes a review, never deletes listings.
        print(app.similar("p0000000"))
        print(app.duplicate("p0000000", "p0000049", threshold=0.95))


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
