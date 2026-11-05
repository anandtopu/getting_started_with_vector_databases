"""Mix two normalized scores.
Run: uv run python modules/14_weaviate/solutions/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(vector, lexical, alpha):
    return alpha * vector + (1 - alpha) * lexical


def main() -> None:
    print(solve(0.9, 0.1, 0.5))


if __name__ == "__main__":
    main()
