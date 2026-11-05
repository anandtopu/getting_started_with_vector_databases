"""Keep the newest record for each ID.
Run: uv run python modules/11_embedded/solutions/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows):
    return dict(rows)


def main() -> None:
    print(solve([["a", 1], ["a", 2]]))


if __name__ == "__main__":
    main()
