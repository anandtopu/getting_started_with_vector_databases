"""Consistent readable search results with scores, useful metadata, and elapsed time."""

from collections.abc import Sequence

from rich.console import Console
from rich.table import Table

from common.stores.types import Hit


def show_hits(
    hits: Sequence[Hit],
    elapsed_ms: float,
    *,
    title: str = "Marlowe Search",
    console: Console | None = None,
) -> None:
    table = Table(title=f"{title} - {elapsed_ms:.2f} ms")
    for column in ("ID", "Score", "Product", "Price", "Region"):
        table.add_column(column)
    for hit in hits:
        price = hit.metadata.get("price")
        table.add_row(
            hit.id,
            f"{hit.score:.4f}",
            str(hit.metadata.get("title", hit.text[:80])),
            f"${price:.2f}" if price is not None else "—",
            str(hit.metadata.get("region", "—")),
        )
    (console or Console()).print(table)
