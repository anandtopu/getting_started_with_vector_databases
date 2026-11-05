"""Apply a tenant filter to every prefetch.
Run: uv run python modules/13_qdrant/solutions/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(branches, tenant):
    return [[key for key in branch if key in tenant] for branch in branches]


def main() -> None:
    print(solve([["a", "b"], ["b"]], {"a"}))


if __name__ == "__main__":
    main()
