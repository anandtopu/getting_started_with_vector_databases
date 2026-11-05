"""Check a reopened collection's identity.
Run: uv run python modules/11_embedded/solutions/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(expected, actual):
    return all(expected.get(k) == actual.get(k) and k in actual for k in ("dim", "space", "metric"))


def main() -> None:
    print(solve({"dim": 3, "space": "a"}, {"dim": 3, "space": "b"}))


if __name__ == "__main__":
    main()
