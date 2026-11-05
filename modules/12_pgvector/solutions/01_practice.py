"""Join eligible seller IDs before limiting.
Run: uv run python modules/12_pgvector/solutions/01_practice.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(rows, sellers, k):
    ranked = sorted((r for r in rows if r[1] in sellers), key=lambda r: (-r[2], r[0]))
    return [r[0] for r in ranked[:k]]


def main() -> None:
    print(solve([["p", "s", 0.9]], ["s"], 1))


if __name__ == "__main__":
    main()
