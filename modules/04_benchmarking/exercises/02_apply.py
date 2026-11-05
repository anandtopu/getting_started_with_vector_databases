"""Compute a linear-interpolated percentile.

Run: uv run python modules/04_benchmarking/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/04_benchmarking/exercises/02_apply.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(values: list[float], percentile: float) -> float:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return sum(values) / len(values)


def main() -> None:
    print(solve([1.0, 2.0, 3.0, 4.0, 100.0], 95.0))


if __name__ == "__main__":
    main()
