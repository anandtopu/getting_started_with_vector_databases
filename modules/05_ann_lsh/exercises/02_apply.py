"""Union candidate buckets.

Run: uv run python modules/05_ann_lsh/exercises/02_apply.py
Check: uv run python scripts/check_exercise.py modules/05_ann_lsh/exercises/02_apply.py
CPU: under a second, local inputs, no models or Docker.
"""


def solve(buckets):
    # YOUR CODE HERE: implement the behavior described in the lesson.
    return list(buckets[0]) if buckets else []


def main():
    print(solve([[1, 2], [2, 3]]))


if __name__ == "__main__":
    main()
