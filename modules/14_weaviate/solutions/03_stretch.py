"""Decide whether generation can run.
Run: uv run python modules/14_weaviate/solutions/03_stretch.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(modules, endpoint):
    return bool(endpoint and "generative-ollama" in modules)


def main() -> None:
    print(solve(["generative-ollama"], True))


if __name__ == "__main__":
    main()
