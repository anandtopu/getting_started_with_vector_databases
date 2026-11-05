"""Find workload mismatches.
Run: uv run python modules/16_landscape/solutions/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(a, b):
    return sorted(k for k in set(a) | set(b) if k not in a or k not in b or a[k] != b[k])


def main() -> None:
    print(solve({"k": 10}, {"k": 5}))


if __name__ == "__main__":
    main()
