"""Asymmetric lookup.

Run: uv run python modules/08_quantization/solutions/02_apply.py
Check: uv run python scripts/check_exercise.py modules/08_quantization/solutions/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(tables, codes):
    return sum(t[c] for t, c in zip(tables, codes, strict=True))


def main():
    print(solve([[0.1, 0.8], [0.4, 0.2]], [1, 0]))


if __name__ == "__main__":
    main()
