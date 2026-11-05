"""Use actual completed requests and wall time for throughput.

Run: uv run python modules/04_benchmarking/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/04_benchmarking/exercises/03_stretch.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(completed: int, wall_seconds: float, latencies_ms: list[float]) -> float:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return len(latencies_ms) / (sum(latencies_ms) / 1000)


def main() -> None:
    print(solve(2, 1.0, [10.0, 10.0]))


if __name__ == "__main__":
    main()
