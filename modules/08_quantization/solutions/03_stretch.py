"""Rescore candidate IDs.

Run: uv run python modules/08_quantization/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/08_quantization/solutions/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(candidates, scores, k):
    return sorted(set(candidates), key=lambda i: (-scores[i], i))[:k]


def main():
    print(solve([2, 0], [0.9, 0.99, 0.4], 1))


if __name__ == "__main__":
    main()
