"""Give duplicate IDs no extra precision credit.

Run: uv run python modules/04_benchmarking/solutions/01_practice.py
Check: uv run python scripts/check_exercise.py modules/04_benchmarking/solutions/01_practice.py
Reference implementation: the same acceptance checks apply to your starter.
CPU: under a second. Tiny fixtures, no models, downloads, or Docker.
"""


def solve(found: list[str], judgments: dict[str, int], k: int) -> float:
    # KEY IDEA: this reference implements the stated acceptance policy.
    if k < 1:
        raise ValueError("k must be positive")
    return sum(judgments.get(key, 0) > 0 for key in set(found[:k])) / k


def main() -> None:
    print(solve(["mug", "mug"], {"mug": 3}, 2))


if __name__ == "__main__":
    main()
