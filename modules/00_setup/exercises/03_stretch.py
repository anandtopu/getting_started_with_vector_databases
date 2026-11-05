"""Choose a minimal local architecture for stated needs.

Run: uv run python modules/00_setup/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/00_setup/exercises/03_stretch.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(count: int, local_updates: bool, concurrent_clients: bool) -> str:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return "server"


def main() -> None:
    print(solve(1000, False, False))


if __name__ == "__main__":
    main()
