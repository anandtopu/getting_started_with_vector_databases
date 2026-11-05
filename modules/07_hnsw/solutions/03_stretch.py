"""Budget adjacency storage.

Run: uv run python modules/07_hnsw/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/07_hnsw/solutions/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(layers):
    return sum(4 * (1 + len(edges)) for layer in layers for edges in layer)


def main():
    print(solve([[[1, 2], [0]], [[1]]]))


if __name__ == "__main__":
    main()
