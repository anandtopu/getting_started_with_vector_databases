"""Merge shard winners.

Run: uv run python modules/09_disk_scale/exercises/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/09_disk_scale/exercises/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(shards, k):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return [row[0] for row in shards[0][:k]] if shards else []


def main():
    print(solve([[[1, 0.4]], [[2, 0.9]]], 1))


if __name__ == "__main__":
    main()
