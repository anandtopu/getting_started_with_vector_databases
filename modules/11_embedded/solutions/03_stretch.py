"""Detect lost or changed rows after restore.
Run: uv run python modules/11_embedded/solutions/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(before, after):
    return sorted(
        k
        for k in set(before) | set(after)
        if k not in before or k not in after or before[k] != after[k]
    )


def main() -> None:
    print(solve({"a": 1, "b": 2}, {"b": 3}))


if __name__ == "__main__":
    main()
