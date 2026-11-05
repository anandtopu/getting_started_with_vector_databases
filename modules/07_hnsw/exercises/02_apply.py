"""Eligible bridge traversal.

Run: uv run python modules/07_hnsw/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/07_hnsw/exercises/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(graph, entry, eligible):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return [entry] if entry in eligible else []


def main():
    print(solve([[1], [2], []], 0, [2]))


if __name__ == "__main__":
    main()
