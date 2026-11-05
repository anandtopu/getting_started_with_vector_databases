"""Use the integrated Marlowe application in a realistic customer flow.

Run: uv run  python modules/20_multimodal/use_case/marlowe.py
Expected: retrieved products or cited policy passages.
CPU: seconds to one minute. Needs: base, prepared Tier 4 artifacts. No implicit downloads.
"""

from common.apps.marlowe import MarloweSearch
from common.pretty import show_hits


def main() -> None:
    with MarloweSearch() as app:
        # KEY IDEA: the same database serves catalog, help and multimodal collections.
        hits = app.photo(product_id="p0000000", image_weight=0.7)
        show_hits(hits, 0, title="Marlowe v5 photo discovery (untimed)")
        assert all(h.id != "p0000000" for h in hits)


if __name__ == "__main__":
    from common.errors import run_cli

    run_cli(main)
