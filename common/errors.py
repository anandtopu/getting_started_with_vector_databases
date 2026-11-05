"""Useful command-line errors without hiding programming failures."""

from collections.abc import Callable

from rich.console import Console


class CourseError(Exception):
    """An expected setup, data, or capability error with an actionable message."""


def run_cli(main: Callable[[], None]) -> None:
    try:
        main()
    except (CourseError, FileNotFoundError, ConnectionError) as exc:
        Console(stderr=True).print(f"[red]{exc}[/red]")
        Console(stderr=True).print("Check setup with: uv run python scripts/check_env.py")
        raise SystemExit(1) from None
