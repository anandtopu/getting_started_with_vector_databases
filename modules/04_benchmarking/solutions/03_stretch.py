"""Use actual completed requests and wall time for throughput.

Run: uv run python modules/04_benchmarking/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/04_benchmarking/solutions/03_stretch.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(completed: int, wall_seconds: float, latencies_ms: list[float]) -> float:
    # KEY IDEA: this reference implements the stated acceptance policy.
    if completed < 0 or wall_seconds <= 0:
        raise ValueError("Need nonnegative completions and positive wall time")
    return completed / wall_seconds


def main() -> None:
    print(solve(2, 1.0, [10.0, 10.0]))


if __name__ == "__main__":
    main()
