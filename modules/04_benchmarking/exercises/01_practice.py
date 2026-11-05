"""Give duplicate IDs no extra precision credit.

Run: uv run python modules/04_benchmarking/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/04_benchmarking/exercises/01_practice.py
Baseline runs before editing; acceptance checks may fail until solved.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(found: list[str], judgments: dict[str, int], k: int) -> float:
    # YOUR CODE HERE: improve the working baseline to meet the README acceptance criteria.
    return sum(judgments.get(key, 0) > 0 for key in found[:k]) / k


def main() -> None:
    print(solve(["mug", "mug"], {"mug": 3}, 2))


if __name__ == "__main__":
    main()
