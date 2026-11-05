"""Use the integrated Marlowe application in a realistic customer flow.

Run: uv run  python modules/17_product_search/use_case/marlowe.py
Expected: retrieved products or cited policy passages.
CPU: seconds to one minute. Needs: base, prepared Tier 4 artifacts. No implicit downloads.
"""

from common.apps.marlowe import MarloweSearch
from common.pretty import show_hits


def main() -> None:
    with MarloweSearch() as app:
        # KEY IDEA: the UI and API use the same application policy.
        result = app.search(query_id="q002")
        show_hits(result.hits, sum(result.timings_ms.values()), title="Marlowe v2")
        print({"filters": result.filter, "warnings": result.warnings})


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
