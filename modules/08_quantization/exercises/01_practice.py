"""Count packed bytes.

Run: uv run python modules/08_quantization/exercises/01_practice.py
Check: uv run python scripts/check_exercise.py modules/08_quantization/exercises/01_practice.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(rows, dimensions, bits):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return rows * dimensions


def main():
    print(solve(3, 10, 1))


if __name__ == "__main__":
    main()
