"""Merge shard winners.

Run: uv run python modules/09_disk_scale/solutions/03_stretch.py
Check: uv run python scripts/check_exercise.py modules/09_disk_scale/solutions/03_stretch.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(shards, k):
    scores = {}
    for shard in shards:
        for key, score in shard:
            scores[key] = max(score, scores.get(key, float("-inf")))
    return sorted(scores, key=lambda key: (-scores[key], key))[:k]


def main():
    print(solve([[[1, 0.4]], [[2, 0.9]]], 1))


if __name__ == "__main__":
    main()
