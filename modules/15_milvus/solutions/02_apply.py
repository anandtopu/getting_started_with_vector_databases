"""Route a partition-key lookup.
Run: uv run python modules/15_milvus/solutions/02_apply.py
CPU: under one second, fixed local inputs. Check with scripts/check_exercise.py.
"""


def solve(partitions, tenant):
    return sorted(k for k, tenants in partitions.items() if tenant in tenants)


def main() -> None:
    print(solve({"a": ["north"], "b": ["south"]}, "north"))


if __name__ == "__main__":
    main()
