"""Budget adjacency storage.

Run: uv run python modules/07_hnsw/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/07_hnsw/exercises/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(layers):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return 4 * len(layers)


def main():
    print(solve([[[1, 2], [0]], [[1]]]))


if __name__ == "__main__":
    main()
