"""Fuse ranked IDs.

Run: uv run python modules/10_filtering_hybrid/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/10_filtering_hybrid/solutions/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(lists, k):
    from tinyvec.hybrid import fuse

    return [key for key, _ in fuse(lists)[:k]]


def main():
    print(solve([["boot", "bag"], ["bag"]], 2))


if __name__ == "__main__":
    main()
