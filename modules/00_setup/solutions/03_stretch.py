"""Choose a minimal local architecture for stated needs.

Run: uv run python modules/00_setup/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/00_setup/solutions/03_stretch.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(count: int, local_updates: bool, concurrent_clients: bool) -> str:
    # KEY IDEA: this reference implements the stated acceptance policy.
    return "server" if concurrent_clients else ("embedded" if local_updates else "library")


def main() -> None:
    print(solve(1000, False, False))


if __name__ == "__main__":
    main()
