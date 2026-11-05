"""Replay deletions on restore.
Return sorted live IDs from [tenant,id] rows after applying [tenant,id] tombstones. A tombstone from a different tenant must not remove a row.
Run: uv run python modules/21_operations/exercises/02_apply.py
CPU: under a second; no downloads or services.
Acceptance: uv run python scripts/check_exercise.py modules/21_operations/exercises/02_apply.py
"""


def solve(rows, tombstones):
    # YOUR CODE HERE: replace the runnable placeholder.
    return None


def main():
    print(solve(*[[["a", "1"], ["b", "2"]], [["a", "1"]]]))


if __name__ == "__main__":
    main()
