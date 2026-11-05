"""Fuse ranked IDs.

Run: uv run python modules/10_filtering_hybrid/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/10_filtering_hybrid/exercises/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(lists, k):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return lists[0][:k] if lists else []


def main():
    print(solve([["boot", "bag"], ["bag"]], 2))


if __name__ == "__main__":
    main()
