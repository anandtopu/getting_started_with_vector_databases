"""Join eligible seller IDs before limiting.
Run: uv run python modules/12_pgvector/exercises/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, sellers, k):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return [r[0] for r in rows[:k]]


def main() -> None:
    print(solve([["p", "s", 0.9]], ["s"], 1))


if __name__ == "__main__":
    main()
