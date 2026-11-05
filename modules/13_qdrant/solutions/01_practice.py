"""Build a region payload posting.
Run: uv run python modules/13_qdrant/solutions/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, region):
    return sorted({key for key, value in rows if value == region})


def main() -> None:
    print(solve([["a", "north"]], "north"))


if __name__ == "__main__":
    main()
