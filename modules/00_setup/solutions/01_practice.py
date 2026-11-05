"""Match phrases without case sensitivity.

Run: uv run python modules/00_setup/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/00_setup/solutions/01_practice.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(rows: list[dict], query: str) -> list[str]:
    # KEY IDEA: this reference implements the stated acceptance policy.
    return [r["id"] for r in rows if query.casefold() in r["text"].casefold()]


def main() -> None:
    print(solve([{"id": "a", "text": "Warm Mug"}], "Warm"))


if __name__ == "__main__":
    main()
