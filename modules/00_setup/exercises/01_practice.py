"""Match phrases without case sensitivity.

Run: uv run python modules/00_setup/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/00_setup/exercises/01_practice.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(rows: list[dict], query: str) -> list[str]:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return [r["id"] for r in rows if query in r["text"]]


def main() -> None:
    print(solve([{"id": "a", "text": "Warm Mug"}], "Warm"))


if __name__ == "__main__":
    main()
