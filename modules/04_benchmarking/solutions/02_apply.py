"""Compute a linear-interpolated percentile.

Run: uv run python modules/04_benchmarking/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/04_benchmarking/solutions/02_apply.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(values: list[float], percentile: float) -> float:
    # KEY IDEA: this reference implements the stated acceptance policy.
    if not values or not 0 <= percentile <= 100:
        raise ValueError("Need observations and percentile 0..100")
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def main() -> None:
    print(solve([1.0, 2.0, 3.0, 4.0, 100.0], 95.0))


if __name__ == "__main__":
    main()
