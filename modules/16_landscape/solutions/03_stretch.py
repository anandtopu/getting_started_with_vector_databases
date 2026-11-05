"""Estimate read and storage cost.
Run: uv run python modules/16_landscape/solutions/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(gib, months, storage_rate, reads, unit_rate):
    return gib * months * storage_rate + reads * unit_rate


def main() -> None:
    print(solve(2, 1, 3, 100, 0.1))


if __name__ == "__main__":
    main()
