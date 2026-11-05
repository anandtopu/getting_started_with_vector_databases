"""Route a partition-key lookup.
Run: uv run python modules/15_milvus/exercises/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(partitions, tenant):
    # YOUR CODE HERE: implement the lesson's acceptance criteria.
    return list(partitions)


def main() -> None:
    print(solve({"a": ["north"], "b": ["south"]}, "north"))


if __name__ == "__main__":
    main()
