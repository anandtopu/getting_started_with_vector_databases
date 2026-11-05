"""Keep the newest record for each ID.
Run: uv run python modules/11_embedded/exercises/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return {k: v for k, v in rows[:1]}


def main() -> None:
    print(solve([["a", 1], ["a", 2]]))


if __name__ == "__main__":
    main()
